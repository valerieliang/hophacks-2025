import numpy as np
import random
import pygame
from collections import deque
from assets.fonts import dynapuff

FRUIT_SIZE = (100, 100)
FRUIT_FOLDER = "assets/fruits/"
MAX_SCORE = 20

class FallingFruit:
    def __init__(self, image, x, y=0, speed=None):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed or random.randint(7, 12)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class AnimalMarchGame:
    def __init__(self, screen, fruit_images):
        self.screen = screen
        self.fruit_images = fruit_images

        # Score & game state
        self.score = 0
        self.max_score = MAX_SCORE
        self.game_over = False
        self.next_screen = None
        self.knee_was_up = False
        self.initialized = False

        # Smoothing with longer history for more stable detection
        self.knee_history_len = 8
        self.left_knee_history = deque(maxlen=self.knee_history_len)
        self.right_knee_history = deque(maxlen=self.knee_history_len)
        
        # Movement detection
        self.march_cooldown = 0  # Prevent multiple triggers
        self.min_cooldown_frames = 15  # Minimum frames between march detections
        
        # Active fruits
        self.falling_fruits = []

        # Debug info
        self.debug_text = ""

    def process_keypoints(self, keypoints):
        """
        keypoints: list of humans, each human is a list of 17 [x, y, conf]
        Only uses hips and knees; ignores missing keypoints
        """
        if not keypoints:
            self.debug_text = "No humans detected"
            return

        kp = keypoints[0]  # Use first human

        # Confidence threshold for detecting a keypoint
        conf_thresh = 0.5
        march_threshold = 30  # Increased threshold for more reliable detection

        # Extract knees and hips with confidence check
        left_knee = kp[13]   # [x, y, conf]
        right_knee = kp[14]  # [x, y, conf]
        left_hip = kp[11]    # [x, y, conf] 
        right_hip = kp[12]   # [x, y, conf]

        # Check if keypoints are valid
        left_knee_valid = left_knee[2] >= conf_thresh
        right_knee_valid = right_knee[2] >= conf_thresh
        left_hip_valid = left_hip[2] >= conf_thresh
        right_hip_valid = right_hip[2] >= conf_thresh

        self.debug_text = f"LK: {left_knee_valid} RK: {right_knee_valid} LH: {left_hip_valid} RH: {right_hip_valid}"

        # Need at least both knees or both hips to be visible
        if not (left_knee_valid and right_knee_valid):
            if not (left_hip_valid and right_hip_valid):
                self.debug_text += " - Insufficient keypoints"
                return

        # Reduce cooldown
        if self.march_cooldown > 0:
            self.march_cooldown -= 1

        # Use knees if available, otherwise use hips
        if left_knee_valid and right_knee_valid:
            left_y = left_knee[1]
            right_y = right_knee[1]
            joint_type = "knee"
        else:
            left_y = left_hip[1]
            right_y = right_hip[1]
            joint_type = "hip"

        # Add to history for smoothing
        self.left_knee_history.append(left_y)
        self.right_knee_history.append(right_y)

        # Calculate smoothed positions
        if len(self.left_knee_history) >= 3 and len(self.right_knee_history) >= 3:
            left_avg = sum(self.left_knee_history) / len(self.left_knee_history)
            right_avg = sum(self.right_knee_history) / len(self.right_knee_history)
            
            # Calculate difference
            height_diff = abs(left_avg - right_avg)
            
            # Check for marching motion
            is_marching = height_diff >= march_threshold
            
            self.debug_text += f" | {joint_type.upper()} diff: {height_diff:.1f}"

            if not self.initialized:
                self.knee_was_up = is_marching
                self.initialized = True
                return

            # Detect march step (transition from not marching to marching)
            if (is_marching and not self.knee_was_up and 
                self.march_cooldown == 0 and self.score < self.max_score):
                
                self.score += 1
                self.march_cooldown = self.min_cooldown_frames
                self.debug_text += f" | MARCH! Score: {self.score}"

                # Spawn a fruit
                fruit_img = random.choice(self.fruit_images)
                x_pos = random.randint(0, self.screen.get_width() - FRUIT_SIZE[0])
                self.falling_fruits.append(FallingFruit(fruit_img, x_pos))

                if self.score >= self.max_score:
                    self.game_over = True
                    self.next_screen = "jungle_win"

            self.knee_was_up = is_marching

    def update_fruits(self):
        """Move fruits down the screen"""
        for fruit in self.falling_fruits[:]:
            fruit.update()
            if fruit.y > self.screen.get_height():
                self.falling_fruits.remove(fruit)

    def draw_fruits(self):
        for fruit in self.falling_fruits:
            fruit.draw(self.screen)

    def draw_debug_info(self):
        """Draw debug information on screen"""
        if self.debug_text:
            debug_font = pygame.font.Font(None, 24)
            debug_surface = debug_font.render(self.debug_text, True, (255, 255, 0))
            self.screen.blit(debug_surface, (10, 100))

    def get_next_screen(self):
        if self.game_over and self.next_screen:
            return self.next_screen
        return None