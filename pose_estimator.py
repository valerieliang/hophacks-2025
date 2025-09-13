from ultralytics import YOLO
import numpy as np

class PoseEstimator:
    def __init__(self, model_path="yolov8n-pose.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """
        Returns:
            annotated_frame: frame with skeleton plotted
            humans_keypoints: list of np.array shape (17, 3) per detected human
                              each keypoint is [x, y, confidence]
        """
        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()

        humans_keypoints = []

        # results[0].keypoints can be None if no humans detected
        if results[0].keypoints is None:
            return annotated_frame, []

        # loop over all detected humans
        for human_kp in results[0].keypoints:
            # human_kp can have shape (N, 3), N <= 17 if partially detected
            # we convert it to shape (17,3), filling missing points with [0,0,0]
            full_kp = np.zeros((17,3), dtype=float)
            n_points = min(len(human_kp), 17)
            full_kp[:n_points] = human_kp[:n_points]
            humans_keypoints.append(full_kp)

        return annotated_frame, humans_keypoints

"""
List of keypoints:
0: nose
1: left_eye
2: right_eye
3: left_ear
4: right_ear
5: left_shoulder
6: right_shoulder
7: left_elbow
8: right_elbow
9: left_wrist
10: right_wrist
11: left_hip
12: right_hip
13: left_knee
14: right_knee
15: left_ankle
16: right_ankle
Keypoint format: [x, y, confidence]
"""