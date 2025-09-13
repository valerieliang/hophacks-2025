from ultralytics import YOLO

class PoseEstimator:
    def __init__(self, model_path="yolov8n-pose.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        # displays skeleton frame with 17 keypoints
        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()
        keypoints = results[0].keypoints  # list of [x, y, conf] per joint
        return annotated_frame, keypoints
