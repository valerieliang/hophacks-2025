import cv2
import numpy as np
from ultralytics import YOLO
import time

POINTS_TO_WIN = 5
FLOOR_POINTS = [(200, 400), (440, 400)]  # Example floor points (x, y)
POINT_RADIUS = 50  # How close (in pixels) a foot must be to a point
RETURN_TO_SELECTOR_DELAY = 2  # Seconds to wait before returning

class RiverCrossingGame:

    def __init__(self):
        self.model = YOLO('yolov8n-pose.pt')
        self.cap = cv2.VideoCapture(0)
        self.score = 0
        self.visited = [False] * len(self.FLOOR_POINTS)

    def feet_positions(self, keypoints):
        # COCO format: 15 = left ankle, 16 = right ankle
        left_ankle = keypoints[15][:2]
        right_ankle = keypoints[16][:2]
        return [tuple(map(int, left_ankle)), tuple(map(int, right_ankle))]

    def check_points(self, feet):
        for i, pt in enumerate(self.FLOOR_POINTS):
            if not self.visited[i]:
                for foot in feet:
                    if np.linalg.norm(np.array(foot) - np.array(pt)) < self.POINT_RADIUS:
                        self.visited[i] = True
                        self.score += 1
                        print(f"Scored! Total: {self.score}")
                        break

    def draw_overlay(self, frame):
        for i, pt in enumerate(self.FLOOR_POINTS):
            color = (0, 255, 0) if self.visited[i] else (0, 0, 255)
            cv2.circle(frame, pt, self.POINT_RADIUS, color, 2)
        cv2.putText(frame, f"Score: {self.score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            results = self.model.predict(frame, conf=0.5)
            if results and results[0].keypoints is not None:
                for kp in results[0].keypoints.xy:
                    feet = self.feet_positions(kp)
                    self.check_points(feet)

            self.draw_overlay(frame)
            cv2.imshow("River Crossing Minigame", frame)

            if self.score >= self.POINTS_TO_WIN:
                cv2.putText(frame, "Minigame Complete!", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 4)
                cv2.imshow("River Crossing Minigame", frame)
                cv2.waitKey(self.RETURN_TO_SELECTOR_DELAY * 1000)
                print("Returning to jungle selector screen...")
                break

            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = RiverCrossingGame()
    game.run()
