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
        self.last_leg_state = None  # track stepping for alternating

    def draw(self):
        self.screen.fill((0, 100, 0))  # jungle green background

        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Pose detection

                # Define target points on the floor for side-to-side steps
                floor_y = self.screen.get_height() - 100  # 100px from bottom
                left_target_x = int(self.screen.get_width() * 0.25)
                right_target_x = int(self.screen.get_width() * 0.75)
                target_radius = 30

                # Draw target circles
                pygame.draw.circle(self.screen, (0, 200, 255), (left_target_x, floor_y), target_radius, 4)
                pygame.draw.circle(self.screen, (255, 100, 0), (right_target_x, floor_y), target_radius, 4)
                
                frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)
                if frame_surface:
                    self.screen.blit(frame_surface, (0, 0))

                    # dummy scoring logic: count stepping
                    try:
                        left_knee_y = keypoints[13][1]
                        right_knee_y = keypoints[14][1]

                        # Detect leg alternation
                        avg_knee_y = (left_knee_y + right_knee_y)/2
                        if self.last_leg_state is None:
                            self.last_leg_state = avg_knee_y
                        else:
                            if avg_knee_y < self.last_leg_state - 20:  # lifted up
                                self.leg_score += 1
                                self.last_leg_state = avg_knee_y
                    except:
                        pass

                    # Display scores
                    score_text = self.font.render(f"Step Points: {self.leg_score}", True, (255, 255, 0))
                    self.screen.blit(score_text, (20, self.screen.get_height()-50))

        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "river_crossing_intro"
        return None
