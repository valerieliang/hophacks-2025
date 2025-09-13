import time

class TreePoseLogic:
    def __init__(self, hold_time=10, knee_threshold=10, stability_threshold=15):
        """
        hold_time: seconds the pose must be held to win
        knee_threshold: minimum y difference to consider a leg lifted
        stability_threshold: max allowed movement for supporting leg
        """
        self.hold_time = hold_time
        self.knee_threshold = knee_threshold
        self.stability_threshold = stability_threshold
        self.in_pose_start = None
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False
        self.last_support_y = None

    def reset(self):
        self.in_pose_start = None
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False
        self.last_support_y = None

    def update(self, keypoints):
        """
        keypoints: dict with 'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
                   each as (x, y)
        Returns: seconds left if countdown active, None otherwise
        """
        required_keys = ['left_knee', 'right_knee', 'left_ankle', 'right_ankle']
        if not all(k in keypoints for k in required_keys):
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False
            self.last_support_y = None
            return None

        # Extract positions
        left_knee_y = keypoints['left_knee'][1]
        right_knee_y = keypoints['right_knee'][1]
        left_ankle_y = keypoints['left_ankle'][1] # ankles
        right_ankle_y = keypoints['right_ankle'][1]

        # Determine which leg is lifted using ankle height
        lifted_leg = None
        support_y = None
        if left_ankle_y < right_knee_y - self.knee_threshold:
            lifted_leg = 'left'
            support_y = right_knee_y
        elif right_ankle_y < left_knee_y - self.knee_threshold:
            lifted_leg = 'right'
            support_y = left_knee_y

        if lifted_leg:
            # Check stability of supporting leg
            if self.last_support_y is None:
                self.last_support_y = support_y
                self.in_pose_start = time.time()
                return None

            if abs(support_y - self.last_support_y) <= self.stability_threshold:
                # Supporting leg is stable
                if not self.timer_start and time.time() - self.in_pose_start >= 1.5:
                    self.timer_start = time.time()
                    self.pose_achieved = True
            else:
                # Supporting leg moved too much, reset buffer
                self.in_pose_start = time.time()
                self.timer_start = None
                self.pose_achieved = False

            self.last_support_y = support_y
        else:
            # Not in pose, reset
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False
            self.last_support_y = None

        # Countdown logic
        if self.timer_start:
            elapsed = time.time() - self.timer_start
            if elapsed >= self.hold_time:
                self.game_over = True
            else:
                return self.hold_time - elapsed

        return None
