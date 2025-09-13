import cv2
import numpy as np
import pygame
from pose_estimator import PoseEstimator

class CameraManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_w, self.screen_h = screen.get_size()
        self.pose_estimator = PoseEstimator()  # 🔑 load pose model once

    def process_frame(self, frame):
        """Convert an OpenCV frame into a pygame surface + keypoints."""
        if frame is None:
            return None, None, None

        # Run pose detection
        annotated_frame, keypoints = self.pose_estimator.detect(frame)

        # Mirror effect
        annotated_frame = cv2.flip(annotated_frame, 1)

        # Keep aspect ratio
        h, w, _ = annotated_frame.shape
        scale = min(self.screen_w / w, self.screen_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        frame_resized = cv2.resize(annotated_frame, (new_w, new_h))

        # Center the frame
        x_offset = (self.screen_w - new_w) // 2
        y_offset = (self.screen_h - new_h) // 2

        # Convert to PyGame surface
        surface = pygame.surfarray.make_surface(np.rot90(frame_resized))

        return surface, (x_offset, y_offset), keypoints

    def get_frame_surface(self, cap):
        # Legacy method: capture frame directly from VideoCapture
        ret, frame = cap.read()
        if not ret:
            return None, None, None
        return self.process_frame(frame)
