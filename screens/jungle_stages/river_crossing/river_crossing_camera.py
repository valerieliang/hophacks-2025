import pygame
import cv2
import threading
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
        self.frame = None
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = RiverCrossingGame()

        # Win overlay image
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button (bottom center)
        screen_w, screen_h = screen.get_size()
        self.menu_button = Button(
            screen,
            text="Back to Menu",
            pos=(screen_w // 2, screen_h - 100),
            size=(300, 80)
        )

        self.score = 0

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
            if self.camera_on and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame, _, self.keypoints = self.camera_manager.process_frame(frame)
            time.sleep(0.01)  # small delay

    def stop_camera_thread(self):
        self._stop_thread = True
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # -------------------- Draw --------------------
    def draw(self):
        # Always fill background
        self.screen.fill((102, 204, 255))

        # Draw camera frame if active
        if self.camera_on and self.frame is not None and not self.game_logic.game_over:
            self.screen.blit(self.frame, (0, 0))
            if self.keypoints is not None:
                self.game_logic.update(self.keypoints)

        elif not self.camera_on and not self.game_logic.game_over:
            pause_font = dynapuff(60)
            pause_text = pause_font.render("Press Camera to Begin", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                     self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # print current score in the bottom right of the screen
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(bottomright=(self.screen.get_width() - 20,
                                                      self.screen.get_height() - 20))

        # Buttons
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # Win overlay and menu button
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0, 0))
            self.menu_button.draw()

        pygame.display.flip()

    # -------------------- Event Handling --------------------
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "river_crossing_intro"

            # Camera toggle (start/stop)
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
                if self.camera_on:
                    # Only start camera thread if turned on
                    self.start_camera_thread()

            # Back to menu button after game over
            if self.game_logic.game_over and self.menu_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "jungle_selector"

        return None
