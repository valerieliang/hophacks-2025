import pygame
import cv2
import numpy as np
from collections import deque
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
import time
from assets.fonts import dynapuff
import random
import os

FRUIT_SIZE = (100, 100)
FRUIT_FOLDER = "assets/fruits/"

class FallingFruit:
    def __init__(self, image, x, y=0, speed=None):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed or random.randint(7, 12)  # faster and slightly varied

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class AnimalMarchCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = cv2.VideoCapture(0)
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.font = dynapuff(40)

        # Camera toggle button
        self.camera_button = CameraToggleButton(screen, size=200)
        self.camera_on = True

        # Score logic
        self.score = 0
        self.max_score = 20
        self.knee_was_up = False
        self.initialized = False

        # Smoothing
        self.knee_history_len = 5
        self.left_knee_history = deque(maxlen=self.knee_history_len)
        self.right_knee_history = deque(maxlen=self.knee_history_len)
        self.threshold = 20  # distance from hip to count as "up"

        # Game over flag
        self.game_over = False

        # Load fruit images
        self.fruits_images = []
        for file in os.listdir(FRUIT_FOLDER):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join(FRUIT_FOLDER, file)).convert_alpha()
                img = pygame.transform.smoothscale(img, FRUIT_SIZE)
                self.fruits_images.append(img)

        # Active falling fruits
        self.falling_fruits = []

    def draw(self):
        self.screen.fill((0, 100, 0))  # jungle green background

        if self.camera_on and self.cap.isOpened() and not self.game_over:
            frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)

            if frame_surface:
                self.screen.blit(frame_surface, (0, 0))

                if keypoints is not None:
                    self.game_logic.process_keypoints(keypoints)
        elif not self.camera_on:
            pause_font = dynapuff(80)
            pause_text = pause_font.render("Paused", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                    self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # Update & draw fruits
        self.game_logic.update_fruits()
        self.game_logic.draw_fruits()

        # Draw score
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        # Draw camera toggle and back button
        self.camera_button.draw()
        self.back_button.draw()

        pygame.display.flip()

        # Automatically go to next screen if game over
        if self.game_logic.game_over:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            return self.game_logic.get_next_screen()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                    cv2.destroyAllWindows()  # just in case
                return "animal_march_intro"
            if self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
                # immediately release camera if turning off
                if not self.camera_on and self.cap and self.cap.isOpened():
                    self.cap.release()
        return None
