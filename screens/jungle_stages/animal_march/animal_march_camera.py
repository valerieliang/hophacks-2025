import pygame
import cv2
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from minigames import animal_march
import numpy as np

class AnimalMarchCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = cv2.VideoCapture(0)
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.font = pygame.font.SysFont("Arial", 32, bold=True)

        self.leg_score = 0
        self.last_step = None  # track last leg lifted ('left' or 'right')

    def draw(self):
        self.screen.fill((0, 100, 0))  # jungle green background

        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
                if frame_surface:
                    self.screen.blit(frame_surface, (0, 0))

                    try:
                        if keypoints is not None:
                            # Convert YOLO Keypoints object to flat numpy array
                            # Only take the first detected person (index 0)
                            kps_array = keypoints[0].xy.cpu().numpy().flatten()
                        else:
                            kps_array = None

                        self.leg_score, self.last_step = animal_march.update_score(
                            kps_array, self.last_step, self.leg_score
                        )

                    except Exception as e:
                        print("Pose update error:", e)

                    # Display score
                    score_text = self.font.render(f"Leg Points: {self.leg_score}", True, (255, 255, 0))
                    self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "animal_march_intro"
        return None
