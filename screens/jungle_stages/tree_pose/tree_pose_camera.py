import pygame
import cv2
import numpy as np
import threading
import time
import os
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button   # generic button
from assets.fonts import dynapuff

class TreePoseCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.font = dynapuff(40)
        self.camera_button = CameraToggleButton(screen, size=200)
        self.camera_on = True

        # Threading
        self.frame = None
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        self.game_logic = None  # Placeholder for game logic

         # Win overlay image
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button (bottom center)
        screen_w, screen_h = screen.get_size()
        self.menu_button = Button(
            screen,
            text="Back to Menu",
            pos=(screen_w // 2, screen_h - 100),  # bottom center
            size=(300, 80)
        )

        # Start camera thread
        self.start_camera_thread()

    def start_camera_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self.cap = cv2.VideoCapture(0)
        self._stop_thread = False
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while not self._stop_thread:
            if self.camera_on and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame, _, self.keypoints = self.camera_manager.process_frame(frame)
            time.sleep(0.01)  # small delay

    def stop_camera(self):
        self._stop_thread = True
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def draw(self):
        self.screen.fill((102, 204, 255))
        pass