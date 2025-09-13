from ultralytics import YOLO

class PoseEstimator:
    def __init__(self, model_path="yolov8n-pose.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        # displays skeleton frame with 17 keypoints
        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()
        # list of [x, y, conf] per joint
        keypoints = results[0].keypoints
        return annotated_frame, keypoints

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