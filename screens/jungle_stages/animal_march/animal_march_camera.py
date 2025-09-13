import pygame
import cv2
import numpy as np
from collections import deque
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from assets.fonts import dynapuff
import random
import os
from minigames.animal_march_logic import *

class AnimalMarchCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = cv2.VideoCapture(0)
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.font = dynapuff(40)

        # Camera toggle
        self.camera_button = CameraToggleButton(screen, size=200)
        self.camera_on = True

        # Load fruits
        self.fruits_images = []
        for file in os.listdir("assets/fruits/"):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join("assets/fruits/", file)).convert_alpha()
                img = pygame.transform.smoothscale(img, FRUIT_SIZE)
                self.fruits_images.append(img)

        # Initialize game logic
        self.game_logic = AnimalMarchGame(screen, self.fruits_images)

    def draw(self):
        self.screen.fill((0, 100, 0))

        if self.camera_on and self.cap.isOpened() and not self.game_logic.game_over:
            frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
            if frame_surface:
                self.screen.blit(frame_surface, (0, 0))
                if keypoints is not None:
                    self.game_logic.process_keypoints(keypoints)

        elif not self.camera_on:
            # Paused
            pause_font = dynapuff(80)
            pause_text = pause_font.render("Paused", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                     self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # Fruits
        self.game_logic.update_fruits()
        self.game_logic.draw_fruits()

        # Score
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        # Buttons
        self.camera_button.draw()
        self.back_button.draw()

        pygame.display.flip()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "animal_march_intro"
            if self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
        return None

    def get_next_screen(self):
        if self.cap:
            self.cap.release()
        return self.game_logic.get_next_screen()