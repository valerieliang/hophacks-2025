import cv2
from ultralytics import YOLO
import numpy as np
import time

# Constants
KNEE_LIFT_THRESHOLD = 0.9  # Ratio of knee y to hip y (lower is higher knee)
STEP_SCORE_TARGET = 10     # Number of steps to finish minigame
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')  # Make sure you have this model

def get_keypoint(kps, idx):
    """Helper to get (x, y, conf) for a keypoint index."""
    if kps is None or len(kps) <= idx * 3 + 2:
        return None
    return kps[idx*3], kps[idx*3+1], kps[idx*3+2]

def is_knee_lifted(kps, side='left'):
    # COCO: 11=left hip, 13=left knee, 12=right hip, 14=right knee
    if side == 'left':
        hip = get_keypoint(kps, 11)
        knee = get_keypoint(kps, 13)
    else:
        hip = get_keypoint(kps, 12)
        knee = get_keypoint(kps, 14)
    if hip is None or knee is None or hip[2] < 0.5 or knee[2] < 0.5:
        return False
    # In image coordinates, y increases downward
    return knee[1] <= hip[1]  # Knee at or above hip

def main():
    cap = cv2.VideoCapture(0)
    score = 0
    last_step = None  # 'left', 'right', or None
    step_cooldown = 0.3  # seconds
    last_step_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run pose estimation
        results = model(frame, verbose=False)
        if results and results[0].keypoints is not None:
            kps = results[0].keypoints.xy[0].cpu().numpy().flatten()
            left_lifted = is_knee_lifted(kps, 'left')
            right_lifted = is_knee_lifted(kps, 'right')

            now = time.time()
            # Detect alternating steps
            if left_lifted and last_step != 'left' and now - last_step_time > step_cooldown:
                score += 1
                last_step = 'left'
                last_step_time = now
            elif right_lifted and last_step != 'right' and now - last_step_time > step_cooldown:
                score += 1
                last_step = 'right'
                last_step_time = now

            # Draw skeleton
            results[0].plot(show=False, conf=False, boxes=False, labels=False, img=frame)

        # Draw score
        cv2.rectangle(frame, (10, 10), (180, 60), (0, 0, 0), -1)
        cv2.putText(frame, f"Score: {score}", (20, 45), FONT, 1.2, (0, 255, 0), 3)

        cv2.imshow('Animal March!', frame)

        # End game if score reached
        if score >= STEP_SCORE_TARGET:
            break

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()

    # Return to jungle_selector (replace with your actual navigation)

if __name__ == "__main__":
    main()