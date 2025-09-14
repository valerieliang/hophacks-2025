from ultralytics import YOLO
import numpy as np

class PoseEstimator:
    def __init__(self, model_path="yolov8n-pose.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """
        Returns:
            annotated_frame: frame with skeleton plotted
            humans_keypoints: list of humans, each is a list of 17 keypoints [x,y,conf]
        """
        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()

        humans_keypoints = []

        if results[0].keypoints is None:
            return annotated_frame, []

        # Access the actual keypoint data properly
        keypoints_data = results[0].keypoints.data  # This is the tensor with keypoint data
        
        if keypoints_data is None or len(keypoints_data) == 0:
            return annotated_frame, []

        # Convert tensor to numpy for easier processing
        keypoints_numpy = keypoints_data.cpu().numpy()

        # loop over detected humans
        for human_idx in range(keypoints_numpy.shape[0]):
            human_keypoints = keypoints_numpy[human_idx]  # Shape: (17, 3) for [x, y, conf]
            
            full_kp = []
            for kp_idx in range(17):  # Ensure we have exactly 17 keypoints
                if kp_idx < len(human_keypoints):
                    x, y, conf = human_keypoints[kp_idx]
                    full_kp.append([float(x), float(y), float(conf)])
                else:
                    full_kp.append([0.0, 0.0, 0.0])  # Fill missing keypoints with zeros
            
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