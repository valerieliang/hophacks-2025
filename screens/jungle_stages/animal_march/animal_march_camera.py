import pygame
import cv2
import numpy as np
from ui.camera_manager import CameraManager
from ui.back_button import BackButton

class AnimalMarchCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = cv2.VideoCapture(0)
        self.camera_on = True
        self.camera_manager = CameraManager(screen)

        w, h = screen.get_size()
        # Back button to return to intro
        self.back_button = BackButton(screen, pos=(60, 60))
        
        # display score
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.leg_score = 0
        self.arm_score = 0
        self.last_leg_state = None  # track up/down for alternating
        self.last_arm_state = None

    def draw(self):
        self.screen.fill((0, 100, 0))  # jungle green background

        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Pose detection
                frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
                if frame_surface:
                    self.screen.blit(frame_surface, (0, 0))

                    # dummy scoring logic: count high knees and arm swings
                    try:
                        left_knee_y = keypoints[13][1]
                        right_knee_y = keypoints[14][1]
                        left_wrist_y = keypoints[17][1]
                        right_wrist_y = keypoints[18][1]

                        # Detect leg alternation
                        avg_knee_y = (left_knee_y + right_knee_y)/2
                        if self.last_leg_state is None:
                            self.last_leg_state = avg_knee_y
                        else:
                            if avg_knee_y < self.last_leg_state - 20:  # lifted up
                                self.leg_score += 1
                                self.last_leg_state = avg_knee_y

                        # Detect wrist up movement
                        avg_wrist_y = (left_wrist_y + right_wrist_y)/2
                        if self.last_arm_state is None:
                            self.last_arm_state = avg_wrist_y
                        else:
                            if avg_wrist_y < self.last_arm_state - 20:
                                self.arm_score += 1
                                self.last_arm_state = avg_wrist_y
                    except:
                        pass

                    # Display scores
                    score_text = self.font.render(f"Leg Points: {self.leg_score}  Arm Points: {self.arm_score}", True, (255, 255, 0))
                    self.screen.blit(score_text, (20, self.screen.get_height()-50))

        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "animal_march_intro"
        return None
