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
                        left_ankle = keypoints[15]
                        right_ankle = keypoints[16]

                        # Check if left foot is near left target and right foot is near right target
                        left_near_left = np.linalg.norm(np.array([left_ankle[0], left_ankle[1]]) - np.array([left_target_x, floor_y])) < target_radius
                        right_near_right = np.linalg.norm(np.array([right_ankle[0], right_ankle[1]]) - np.array([right_target_x, floor_y])) < target_radius

                        # Check if right foot is near right target and left foot is near left target (alternating)
                        right_near_left = np.linalg.norm(np.array([right_ankle[0], right_ankle[1]]) - np.array([left_target_x, floor_y])) < target_radius
                        left_near_right = np.linalg.norm(np.array([left_ankle[0], left_ankle[1]]) - np.array([right_target_x, floor_y])) < target_radius

                        # Alternating step detection
                        current_leg_state = None
                        if left_near_left and not right_near_right:
                            current_leg_state = "left"
                        elif right_near_right and not left_near_left:
                            current_leg_state = "right"

                        if current_leg_state and current_leg_state != self.last_leg_state:
                            self.leg_score += 1
                            self.last_leg_state = current_leg_state
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
