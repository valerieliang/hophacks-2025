import pygame
import cv2
import threading
import time
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button
from assets.fonts import dynapuff
from minigames.tree_pose_logic import TreePoseLogic

class TreePoseCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.camera_button = CameraToggleButton(screen, size=200)
        self.font = dynapuff(40)
        self.camera_on = True

        # Threading
        self.frame_surface = None
        self.frame_offset = (0, 0)
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = TreePoseLogic(hold_time=10)

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

    def draw(self):
        # Always fill background
        self.screen.fill((102, 204, 255))

        # Draw camera frame if available
        if self.camera_on and self.frame_surface:
            self.screen.blit(self.frame_surface, self.frame_offset)

        # Draw buttons
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # Draw countdown timer if pose detected and not yet completed
        if self.game_logic.pose_achieved and not self.game_logic.game_over:
            seconds_left = self.game_logic.update(self.keypoints)
            if seconds_left is not None:
                text_surf = self.font.render(f"Hold: {int(seconds_left)}s", True, (255, 0, 0))
                rect = text_surf.get_rect(center=(self.screen.get_width() // 2, 100))
                self.screen.blit(text_surf, rect)

        # Draw win overlay if game is completed
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0, 0))
            self.menu_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "tree_pose_intro"

            # Camera toggle only if game is not over
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on

        return None

    def start_camera_thread(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self._stop_thread = False
        self._thread = threading.Thread(target=self.camera_loop, daemon=True)
        self._thread.start()

    def stop_camera_thread(self):
        self._stop_thread = True
        if self._thread and self._thread.is_alive():
            self._thread.join()
        if self.cap:
            self.cap.release()
            self.cap = None

    def camera_loop(self):
        while not self._stop_thread and self.cap.isOpened():
            # Get processed frame and keypoints from CameraManager
            frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
            if frame_surface is not None:
                self.frame_surface = frame_surface
                self.frame_offset = offset
                self.keypoints = keypoints

            # Update game logic
            self.game_logic.update(self.keypoints)

            time.sleep(0.03)
