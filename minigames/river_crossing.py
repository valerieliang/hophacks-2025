import cv2
import numpy as np
from ultralytics import YOLO
import time

# --- CONFIGURATION ---
POINTS_TO_WIN = 5
FLOOR_POINTS = [(200, 400), (440, 400)]  # Example floor points (x, y)
POINT_RADIUS = 50  # How close (in pixels) a foot must be to a point
RETURN_TO_SELECTOR_DELAY = 2  # Seconds to wait before returning

# --- INITIALIZATION ---
model = YOLO('yolov8n-pose.pt')  # Make sure you have this model downloaded
cap = cv2.VideoCapture(0)
score = 0
visited = [False] * len(FLOOR_POINTS)

def feet_positions(keypoints):
    # COCO format: 15 = left ankle, 16 = right ankle
    left_ankle = keypoints[15][:2]
    right_ankle = keypoints[16][:2]
    return [tuple(map(int, left_ankle)), tuple(map(int, right_ankle))]

def check_points(feet, floor_points, visited):
    global score
    for i, pt in enumerate(floor_points):
        if not visited[i]:
            for foot in feet:
                if np.linalg.norm(np.array(foot) - np.array(pt)) < POINT_RADIUS:
                    visited[i] = True
                    score += 1
                    print(f"Scored! Total: {score}")
                    break

def draw_overlay(frame, floor_points, visited, score):
    for i, pt in enumerate(floor_points):
        color = (0, 255, 0) if visited[i] else (0, 0, 255)
        cv2.circle(frame, pt, POINT_RADIUS, color, 2)
    cv2.putText(frame, f"Score: {score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

def main():
    global score, visited
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=0.5)
        if results and results[0].keypoints is not None:
            for kp in results[0].keypoints.xy:
                feet = feet_positions(kp)
                check_points(feet, FLOOR_POINTS, visited)

        draw_overlay(frame, FLOOR_POINTS, visited, score)
        cv2.imshow("River Crossing Minigame", frame)

        if score >= POINTS_TO_WIN:
            cv2.putText(frame, "Minigame Complete!", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 4)
            cv2.imshow("River Crossing Minigame", frame)
            cv2.waitKey(RETURN_TO_SELECTOR_DELAY * 1000)
            print("Returning to jungle selector screen...")
            break # I'm really not sure if this even does anything 

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    main()