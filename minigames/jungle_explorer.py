import cv2
import mediapipe as mp
import subprocess

# Parameters
POINTS_TO_WIN = 10

# Initialize MediaPipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# State variables
points = 0
squat_in_progress = False

# Helper function to detect squat and jump with arms up
def detect_squat_jump_with_arms_up(landmarks):
    # Get relevant landmarks
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

    # Calculate average y positions (normalized)
    avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    avg_wrist_y = (left_wrist.y + right_wrist.y) / 2
    avg_hip_y = (left_hip.y + right_hip.y) / 2
    avg_knee_y = (left_knee.y + right_knee.y) / 2
    avg_ankle_y = (left_ankle.y + right_ankle.y) / 2

    # Heuristic: squat if hips are close to knees, jump if hips are high, arms up if wrists above shoulders
    is_squat = avg_hip_y > avg_knee_y - 0.05
    is_jump = avg_hip_y < avg_shoulder_y - 0.1
    arms_up = (left_wrist.y < left_shoulder.y - 0.05) and (right_wrist.y < right_shoulder.y - 0.05)

    return is_squat, is_jump, arms_up

# Open webcam
cap = cv2.VideoCapture(0)

print("Jungle Explorer Minigame Started! Do a squat and jump with arms up to grab vines.")

while cap.isOpened() and points < POINTS_TO_WIN:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip for selfie view
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        is_squat, is_jump, arms_up = detect_squat_jump_with_arms_up(landmarks)

        if is_squat and arms_up:
            squat_in_progress = True
            cv2.putText(frame, "Squat detected! Prepare to jump!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        elif squat_in_progress and is_jump and arms_up:
            points += 1
            squat_in_progress = False
            cv2.putText(frame, f"Vine grabbed! Points: {points}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        elif not is_squat and not is_jump:
            squat_in_progress = False

    cv2.putText(frame, f"Points: {points}/{POINTS_TO_WIN}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.imshow('Jungle Explorer', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break
        # When the minigame ends, return to the jungle_selector screen
        break
    subprocess.Popen(["python", "jungle_selector.py"])
if points >= POINTS_TO_WIN:
    print("Congratulations! You completed the Jungle Explorer minigame!")

cap.release()
cv2.destroyAllWindows()