from ultralytics import YOLO

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

        # loop over detected humans
        for human_kp in results[0].keypoints:
            full_kp = [[0,0,0]]*17  # initialize with zeros
            for i, kp in enumerate(human_kp):
                if i >= 17:
                    break
                full_kp[i] = list(kp)  # convert ndarray to list
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