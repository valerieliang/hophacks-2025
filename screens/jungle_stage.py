import pygame
import cv2
from ui.buttons import Button
from ui.camera_manager import CameraManager
from ui.back_button import BackButton

class JungleStage:
    def __init__(self, screen):
        self.screen = screen
        self.camera_on = False
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen)

        w, h = screen.get_size()
        self.toggle_button = Button(
            screen,
            image="assets/camera_button.png",
            pos=(w // 2, h - 80),
            size=(128, 128)
        )
        self.last_keypoints = None

    def draw(self):
        self.screen.fill((0, 100, 0))

        if self.camera_on and self.cap:
            result = self.camera_manager.get_frame_surface(self.cap)
            if result:
                frame_surface, (x, y), keypoints = result
                self.last_keypoints = keypoints
                self.screen.blit(frame_surface, (x, y))

        self.toggle_button.draw()
        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_selector"  # go back to stage select
            if self.toggle_button.is_clicked(mouse_pos):
                if self.camera_on:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    self.camera_on = False
                else:
                    self.cap = cv2.VideoCapture(0)
                    if self.cap.isOpened():
                        self.camera_on = True
        return None
