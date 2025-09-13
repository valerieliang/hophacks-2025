import cv2
import numpy as np
import pygame
from pose_estimator import PoseEstimator

class CameraManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.cap = None
        self.pose_estimator = PoseEstimator()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            raise RuntimeError("Failed to open camera")
        return self.cap

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_frame_surface(self):
        # Returns the latest frame as a scaled/fitted PyGame surface
        if not self.cap or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        annotated_frame, keypoints = self.pose_estimator.detect(frame)
        frame_height, frame_width = annotated_frame.shape[:2]

        # Aspect ratio scaling
        screen_ratio = self.screen_width / self.screen_height
        frame_ratio = frame_width / frame_height

        if frame_ratio > screen_ratio:
            new_width = self.screen_width
            new_height = int(self.screen_width / frame_ratio)
        else:
            new_height = self.screen_height
            new_width = int(self.screen_height * frame_ratio)

        frame_resized = cv2.resize(annotated_frame, (new_width, new_height))
        frame_resized = cv2.flip(frame_resized, 1)

        surface = pygame.surfarray.make_surface(np.rot90(frame_resized))
        x_offset = (self.screen_width - new_width) // 2
        y_offset = (self.screen_height - new_height) // 2

        return surface, x_offset, y_offset
