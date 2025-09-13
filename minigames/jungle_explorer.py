import cv2
from ultralytics import YOLO
import time

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')

# Game parameters
POINTS_TO_WIN = 5

def is_squat(keypoints):
    # Check if hips are below knees (simple squat detection)
    left_hip = keypoints[11]
    right_hip = keypoints[12]
    left_knee = keypoints[13]
    right_knee = keypoints[14]
    # y increases downward in image coordinates
    return (left_hip[1] > left_knee[1] and right_hip[1] > right_knee[1])

def is_jump_with_arms_up(keypoints):
    # Check if both wrists are above head (simple arms up detection)
    left_wrist = keypoints[9]
    right_wrist = keypoints[10]
    head = keypoints[0]
    return (left_wrist[1] < head[1] and right_wrist[1] < head[1])

def main():
    cap = cv2.VideoCapture(0)
    points = 0
    squat_detected = False
    jump_detected = False
    last_action_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        if results and results[0].keypoints is not None:
            for kp in results[0].keypoints.xy:
                keypoints = kp.cpu().numpy()
                # Detect squat
                if is_squat(keypoints):
                    squat_detected = True
                    jump_detected = False
                # Detect jump with arms up after squat
                elif squat_detected and is_jump_with_arms_up(keypoints):
                    if not jump_detected and time.time() - last_action_time > 1:
                        points += 1
                        print(f"Vine caught! Points: {points}")
                        last_action_time = time.time()
                        jump_detected = True
                        squat_detected = False

        # Display points on frame
        cv2.putText(frame, f"Points: {points}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
        cv2.imshow("Jungle Explorer", frame)

        # Check for win
        if points >= POINTS_TO_WIN:
            print("Minigame complete! Returning to jungle selector...")
            break

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()
    # Here, return to jungle selector screen (implement as needed)

if __name__ == "__main__":
    main()