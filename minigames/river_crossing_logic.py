import cv2
import numpy as np
from ultralytics import YOLO

POINTS_TO_WIN = 5
FLOOR_POINTS = [(200, 400), (440, 400)]
POINT_RADIUS = 50

class RiverCrossingGame:
    def __init__(self, points_to_win=POINTS_TO_WIN):
        self.model = YOLO('yolov8n-pose.pt')
        self.score = 0
        self.visited = [False] * len(FLOOR_POINTS)
        self.game_over = False
        self.points_to_win = points_to_win

    def check_points(self, feet):
        for i, pt in enumerate(FLOOR_POINTS):
            if not self.visited[i]:
                for foot in feet:
                    if np.linalg.norm(np.array(foot) - np.array(pt)) < POINT_RADIUS:
                        self.visited[i] = True
                        self.score += 1
                        print(f"Scored! Total: {self.score}")
                        if self.score >= self.points_to_win:
                            self.game_over = True
                        break

    def feet_positions(self, keypoints):
        """Return left and right ankle positions if detected, else None."""
        if keypoints.shape[0] <= 16:  # not enough keypoints detected
            return None
        left_ankle = keypoints[15][:2]
        right_ankle = keypoints[16][:2]
        return [tuple(map(int, left_ankle)), tuple(map(int, right_ankle))]

    def update(self, keypoints_list):
        """
        Update game state with a list of keypoints (from YOLO detections).
        Skips if keypoints are missing.
        """
        if self.game_over or keypoints_list is None:
            return

        for kp in keypoints_list:
            feet = self.feet_positions(kp)
            if feet is None:
                continue  # Skip if person is partially out of frame
            self.check_points(feet)