import pygame
import cv2
import numpy as np
from collections import deque
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
import time
from assets.fonts import dynapuff

class AnimalMarchCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = cv2.VideoCapture(0)
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.font = dynapuff(40) 

        # Camera toggle button
        self.camera_button = CameraToggleButton(screen, size=200)
        self.camera_on = True

        # Score logic
        self.score = 0
        self.max_score = 20
        self.knee_was_up = False
        self.initialized = False

        # Smoothing
        self.knee_history_len = 5
        self.left_knee_history = deque(maxlen=self.knee_history_len)
        self.right_knee_history = deque(maxlen=self.knee_history_len)
        self.threshold = 30  # distance from hip to count as "up"

        # Game over flag
        self.game_over = False

    def draw(self):
        self.screen.fill((0, 100, 0))  # jungle green background

        if self.camera_on and self.cap.isOpened() and not self.game_over:
            frame_surface, offset, keypoints = self.camera_manager.get_frame_surface(self.cap)

            if frame_surface:
                self.screen.blit(frame_surface, (0, 0))

                if keypoints is not None:
                    kps = keypoints.xy[0].cpu().numpy()
                    if kps.shape[0] >= 15:
                        left_hip_y = kps[11][1]
                        right_hip_y = kps[12][1]
                        left_knee_y = kps[13][1]
                        right_knee_y = kps[14][1]

                        # Smooth knee positions
                        self.left_knee_history.append(left_knee_y)
                        self.right_knee_history.append(right_knee_y)

                        left_knee_avg = np.mean(self.left_knee_history)
                        right_knee_avg = np.mean(self.right_knee_history)

                        # Knee up if either knee is near the hip
                        knee_up = (left_knee_avg < left_hip_y + self.threshold or
                                   right_knee_avg < right_hip_y + self.threshold)

                        if not self.initialized:
                            self.knee_was_up = knee_up
                            self.initialized = True
                        else:
                            if knee_up and not self.knee_was_up and self.score < self.max_score:
                                self.score += 1
                                self.knee_was_up = True
                                # Immediate update
                                self.update_score_display()
                                if self.score >= self.max_score:
                                    self.game_over = True
                                    print("You win!")
                            elif not knee_up:
                                self.knee_was_up = False

                        # Debug
                        print(f"Left knee: {left_knee_avg:.1f}, Right knee: {right_knee_avg:.1f}, "
                              f"Knee up: {knee_up}, Score: {self.score}")

        # Display score (always white)
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))

        # Draw camera toggle and back button
        self.camera_button.draw()
        self.back_button.draw()

        pygame.display.flip()

    def update_score_display(self):
        # Redraw score immediately
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, self.screen.get_height() - 50))
        pygame.display.update(pygame.Rect(20, self.screen.get_height() - 50, 200, 40))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                if self.cap:
                    self.cap.release()
                return "animal_march_intro"

            if self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on

        return None
