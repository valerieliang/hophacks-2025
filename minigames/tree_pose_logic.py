import time

class TreePoseLogic:
    def __init__(self, hold_time=10, knee_threshold=20, stability_threshold=10):
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
        keypoints: dict with 'left_knee' and 'right_knee', each (x, y)
        Returns: seconds left if countdown active, None otherwise
        """
        if 'left_knee' not in keypoints or 'right_knee' not in keypoints:
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False
            self.last_support_y = None
            return None

        left_knee_y = keypoints['left_knee'][1]
        right_knee_y = keypoints['right_knee'][1]

        # Determine which leg is lifted
        if left_knee_y < right_knee_y - self.knee_threshold:
            lifted_leg = 'left'
            support_y = right_knee_y
        elif right_knee_y < left_knee_y - self.knee_threshold:
            lifted_leg = 'right'
            support_y = left_knee_y
        else:
            lifted_leg = None
            support_y = None

        if lifted_leg:
            # Check if supporting leg is stable
            if self.last_support_y is None:
                self.last_support_y = support_y
                self.in_pose_start = time.time()  # start buffer
                return None

            if abs(support_y - self.last_support_y) <= self.stability_threshold:
                # Supporting leg is stable
                if not self.timer_start and time.time() - self.in_pose_start >= 2:
                    self.timer_start = time.time()
                    self.pose_achieved = True
            else:
                # Supporting leg moved too much, reset
                self.in_pose_start = time.time()
                self.timer_start = None
                self.pose_achieved = False

            self.last_support_y = support_y
        else:
            # Not standing on one leg, reset
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False
            self.last_support_y = None

        # Update countdown
        if self.timer_start:
            elapsed = time.time() - self.timer_start
            if elapsed >= self.hold_time:
                self.game_over = True
            else:
                return self.hold_time - elapsed

        return None
