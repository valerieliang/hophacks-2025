import pygame
import cv2
import threading
import numpy as np
import time
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button
from assets.fonts import dynapuff
from minigames.river_crossing_logic import RiverCrossingGame

class RiverCrossingCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.camera_button = CameraToggleButton(screen, size=200)
        self.font = dynapuff(40)
        self.camera_on = False

        # Threading
        self.surface = None
        self.offset = (0, 0)
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = RiverCrossingGame()

        # Win overlay
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button
        screen_w, screen_h = screen.get_size()
        self.menu_button = Button(
            screen,
            text="Back to Menu",
            pos=(screen_w // 2, screen_h - 100),  # bottom center
            size=(300, 80)
        )

    # -------------------- Camera Thread --------------------
    def start_camera_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self.cap = cv2.VideoCapture(0)
        self._stop_thread = False
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while not self._stop_thread:
            if self.camera_on and self.cap is not None and self.cap.isOpened():
                try:
                    surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
                    if surface is not None:
                        self.surface = surface
                        self.offset = offset
                        self.keypoints = keypoints
                except Exception as e:
                    print(f"Error processing frame: {e}")
            time.sleep(0.01)

    def stop_camera_thread(self):
        self._stop_thread = True
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # -------------------- Draw --------------------
    def draw(self):
        self.screen.fill((102, 204, 255))

        if self.camera_on and self.surface and not self.game_logic.game_over:
            # Draw camera surface centered
            self.screen.blit(self.surface, self.offset)

            # Draw stepping stone (one at a time)
            if self.keypoints:
                # Align next stone with average ankle Y
                for kp in self.keypoints:
                    feet = self.game_logic.feet_positions(kp)
                    if feet:
                        avg_y = sum(f[1] for f in feet)//len(feet)
                        self.game_logic.update_stone_y(avg_y)
                        self.game_logic.check_stones(feet)

            # Draw keypoints
            if self.keypoints:
                for kp in self.keypoints:
                    feet = self.game_logic.feet_positions(kp)
                    if feet:
                        for fx, fy in feet:
                            # Add offset from camera centering
                            ox, oy = self.offset
                            pygame.draw.circle(self.screen, (255, 255, 0), (fx+ox, fy+oy), 15)

            # Draw next stone on screen
            self.game_logic.draw_stone_on_surface(self.screen, self.offset)

        elif not self.camera_on and not self.game_logic.game_over:
            pause_font = dynapuff(60)
            text = pause_font.render("Press Camera to Begin", True, (255,255,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255,255,255))
        score_rect = score_text.get_rect(bottomright=(self.screen.get_width()-20, self.screen.get_height()-20))
        self.screen.blit(score_text, score_rect)

        # Draw buttons
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # Win overlay
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0,0))
            self.menu_button.draw()

        pygame.display.flip()

    # -------------------- Event Handling --------------------
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "river_crossing_intro"
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
                if self.camera_on:
                    self.start_camera_thread()
            if self.game_logic.game_over and self.menu_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "jungle_selector"
        return None
