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
from minigames.animal_march_logic import *

FRUIT_SIZE = (100, 100)

class AnimalMarchCamera:
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

        # Load fruits
        self.fruits_images = []
        for file in os.listdir("assets/fruits/"):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join("assets/fruits/", file)).convert_alpha()
                img = pygame.transform.smoothscale(img, FRUIT_SIZE)
                self.fruits_images.append(img)

        # Game logic
        self.game_logic = AnimalMarchGame(screen, self.fruits_images)

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
        self.screen.fill((0, 100, 0))

        # --- Draw camera frame if active ---
        if self.camera_on and self.frame is not None and not self.game_logic.game_over:
            self.screen.blit(self.frame, (0, 0))
            if self.keypoints is not None:
                self.game_logic.process_keypoints(self.keypoints)
        elif not self.camera_on and not self.game_logic.game_over:
            pause_font = dynapuff(80)
            pause_text = pause_font.render("Paused", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                     self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # --- Game elements ---
        self.game_logic.update_fruits()
        self.game_logic.draw_fruits()

        # Score
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        # Buttons
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # --- Win Overlay ---
        if self.game_logic.game_over or not self.camera_on:
            # Draw full-screen win image
            self.screen.blit(self.win_image, (0, 0))

            # Draw Back to Menu button
            self.menu_button.draw()

        # Always draw back button in corner
        self.back_button.draw()

        pygame.display.flip()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera()
                return "animal_march_intro"

            # Camera toggle only if game is not over
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on

            # Back to Menu button (after game over / camera off)
            if (self.game_logic.game_over or not self.camera_on) and self.menu_button.is_clicked(mouse_pos):
                self.stop_camera()
                return "jungle_selector"  # go back to main menu

        return None
