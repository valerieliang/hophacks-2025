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
        self.surface = None
        self.offset = (0,0)
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = RiverCrossingGame()

        # Win overlay
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button
        sw, sh = screen.get_size()
        self.menu_button = Button(screen, text="Back to Menu", pos=(sw//2, sh-100), size=(300, 80))

    # --- Camera Thread ---
    def start_camera_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self.cap = cv2.VideoCapture(0)
        self._stop_thread = False
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while not self._stop_thread:
            if self.camera_on and self.cap and self.cap.isOpened():
                try:
                    surface, offset, humans_keypoints = self.camera_manager.get_frame_surface(self.cap)
                    if surface is not None:
                        self.surface = surface
                        self.offset = offset
                        # always store as list of humans (list of lists)
                        if humans_keypoints is None:
                            self.keypoints = []
                        else:
                            cleaned = []
                            for kp in humans_keypoints:
                                # make sure each human is list of 17 keypoints
                                if len(kp) < 17:
                                    kp = kp + [[0,0,0]]*(17 - len(kp))
                                cleaned.append(kp)
                            self.keypoints = cleaned
                except Exception as e:
                    print(f"Error processing frame: {e}")
            time.sleep(0.01)



    def stop_camera_thread(self):
        self._stop_thread = True
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # --- Draw ---
    def draw(self):
        self.screen.fill((102,204,255))

        if self.camera_on and self.surface:
            # --- Update game logic each frame ---
            if self.keypoints:
                self.game_logic.update(self.keypoints)

            # --- Draw camera ---
            self.screen.blit(self.surface, self.offset)

            # --- Draw keypoints ---
            for kp in (self.keypoints or []):
                feet = self.game_logic.feet_positions(kp)
                if feet:
                    ox, oy = self.offset
                    for fx, fy in feet:
                        pygame.draw.circle(self.screen, (255,255,0), (fx+ox, fy+oy), 15)

            # --- Draw next stone ---
            self.game_logic.draw_stone_on_surface(self.screen, self.offset)

        elif not self.camera_on and not self.game_logic.game_over:
            text_font = dynapuff(60)
            text = text_font.render("Press Camera to Begin", True, (255,255,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, rect)

        # --- Score ---
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255,255,255))
        score_rect = score_text.get_rect(bottomright=(self.screen.get_width()-20, self.screen.get_height()-20))
        self.screen.blit(score_text, score_rect)

        # --- Buttons ---
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # --- Win overlay ---
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0,0))
            self.menu_button.draw()

        pygame.display.flip()

    # --- Event Handling ---
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
