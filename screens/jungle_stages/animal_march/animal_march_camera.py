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
MAX_SCORE = 2  # number of knee lifts to win

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
        self.max_score = MAX_SCORE 
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
                    kps = keypoints.xy[0].cpu().numpy()
                    if kps.shape[0] >= 15:
                        left_hip_y = kps[11][1]
                        right_hip_y = kps[12][1]
                        left_knee_y = kps[13][1]
                        right_knee_y = kps[14][1]

                        # Smooth knee positions
                        self.left_knee_history.append(left_knee_y)
                        self.right_knee_history.append(right_knee_y)

                        left_knee_avg = np.mean(self.left_knee_history)
                        right_knee_avg = np.mean(self.right_knee_history)

                        # Knee up if either knee is near the hip
                        knee_up = (left_knee_avg < left_hip_y + self.threshold or
                                   right_knee_avg < right_hip_y + self.threshold)

                        if not self.initialized:
                            self.knee_was_up = knee_up
                            self.initialized = True
                        else:
                            if knee_up and not self.knee_was_up and self.score < self.max_score:
                                self.score += 1
                                self.knee_was_up = True
                                # Spawn a random fruit at random x position
                                fruit_img = random.choice(self.fruits_images)
                                x_pos = random.randint(0, self.screen.get_width() - FRUIT_SIZE[0])
                                self.falling_fruits.append(FallingFruit(fruit_img, x_pos))
                                self.update_score_display()

                                if self.score >= self.max_score and not self.game_over:
                                    self.game_over = True
                                    # Immediately signal main loop to switch to win screen
                                    self.next_screen = "jungle_win"

                            elif not knee_up:
                                self.knee_was_up = False

        elif not self.camera_on:
            # Show Paused text in the middle
            pause_font = dynapuff(80)
            pause_text = pause_font.render("Paused", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                     self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # Update and draw falling fruits
        for fruit in self.falling_fruits[:]:
            fruit.update()
            fruit.draw(self.screen)
            if fruit.y > self.screen.get_height():
                self.falling_fruits.remove(fruit)

        # Display score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        # Draw camera toggle and back button
        self.camera_button.draw()
        self.back_button.draw()

        pygame.display.flip()

    def update_score_display(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))
        pygame.display.update(pygame.Rect(20, self.screen.get_height() - 50, 200, 40))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "animal_march_intro"
            if self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on

        # If game over, return next screen immediately
        if getattr(self, "game_over", False) and getattr(self, "next_screen", None):
            if self.cap:
                self.cap.release()
            return self.next_screen

        return None