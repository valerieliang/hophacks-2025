import time
import numpy as np

class TreePoseLogic:
    def __init__(self, hold_time=10, lift_threshold=40):
        """
        hold_time: seconds required to win
        lift_threshold: pixels ankle must be above knee
        """
        self.hold_time = hold_time
        self.lift_threshold = lift_threshold
        self.start_time = None
        self.has_won = False

    def update(self, keypoints):
        if self.has_won:
            return True

        if keypoints is None or len(keypoints.xy) == 0:
            self.start_time = None
            return False

        # Get first person’s keypoints
        pts = keypoints.xy[0]  # shape (17, 2)
        left_knee, right_knee = pts[13], pts[14]
        left_ankle, right_ankle = pts[15], pts[16]

        valid_pose = False

        # Check if left ankle is lifted higher (y smaller) than left knee
        if left_ankle[1] < left_knee[1] - self.lift_threshold:
            valid_pose = True

        # Or if right ankle is lifted
        if right_ankle[1] < right_knee[1] - self.lift_threshold:
            valid_pose = True

        if valid_pose:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                elapsed = time.time() - self.start_time
                if elapsed >= self.hold_time:
                    self.has_won = True
                    return True
        else:
            # Reset if they drop the pose
            self.start_time = None

        return False

    def reset(self):
        self.start_time = None
        self.has_won = False
