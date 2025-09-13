import time

class TreePoseLogic:
    def __init__(self, hold_time=10):
        """
        hold_time: seconds the pose must be held to win
        """
        self.hold_time = hold_time
        self.in_pose_start = None  # when user entered pose
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False

    def reset(self):
        self.in_pose_start = None
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False

    def update(self, keypoints):
        """
        keypoints: dict with 'left_knee' and 'right_knee', each (x, y)
        Returns: seconds left if countdown active, None otherwise
        """
        if 'left_knee' not in keypoints or 'right_knee' not in keypoints:
            self.in_pose_start = None
            self.timer_start = None
            return None

        left_knee_y = keypoints['left_knee'][1]
        right_knee_y = keypoints['right_knee'][1]

        # Check if one knee is higher than the other
        if abs(left_knee_y - right_knee_y) > 20:  # require noticeable difference
            if not self.in_pose_start:
                # start 2-second buffer
                self.in_pose_start = time.time()
            elif time.time() - self.in_pose_start >= 2 and not self.timer_start:
                # start countdown after buffer
                self.timer_start = time.time()
                self.pose_achieved = True
        else:
            # not in pose, reset
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False

        # Update countdown
        if self.timer_start:
            elapsed = time.time() - self.timer_start
            if elapsed >= self.hold_time:
                self.game_over = True
            else:
                return self.hold_time - elapsed

        return None
