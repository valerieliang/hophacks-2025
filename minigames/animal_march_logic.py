import numpy as np
import random
from collections import deque
from screens.jungle_stages.animal_march.animal_march_camera import *
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

        # Smoothing
        self.knee_history_len = 5
        self.left_knee_history = deque(maxlen=self.knee_history_len)
        self.right_knee_history = deque(maxlen=self.knee_history_len)
        self.threshold = 20

        # Active fruits
        self.falling_fruits = []

    def process_keypoints(self, keypoints):
        """Update game state based on current keypoints"""
        kps = keypoints.xy[0].cpu().numpy()
        if kps.shape[0] < 15:
            return

        left_hip_y = kps[11][1]
        right_hip_y = kps[12][1]
        left_knee_y = kps[13][1]
        right_knee_y = kps[14][1]

        # Smooth
        self.left_knee_history.append(left_knee_y)
        self.right_knee_history.append(right_knee_y)
        left_knee_avg = np.mean(self.left_knee_history)
        right_knee_avg = np.mean(self.right_knee_history)

        # Check if knee is up
        knee_up = (left_knee_avg < left_hip_y + self.threshold or
                   right_knee_avg < right_hip_y + self.threshold)

        if not self.initialized:
            self.knee_was_up = knee_up
            self.initialized = True
            return

        if knee_up and not self.knee_was_up and self.score < self.max_score:
            self.score += 1
            self.knee_was_up = True

            # Spawn a fruit
            fruit_img = random.choice(self.fruit_images)
            x_pos = random.randint(0, self.screen.get_width() - FRUIT_SIZE[0])
            self.falling_fruits.append(FallingFruit(fruit_img, x_pos))

            # Check for win
            if self.score >= self.max_score:
                self.game_over = True
                self.next_screen = "jungle_win"

        elif not knee_up:
            self.knee_was_up = False

    def update_fruits(self):
        """Move fruits down the screen"""
        for fruit in self.falling_fruits[:]:
            fruit.update()
            if fruit.y > self.screen.get_height():
                self.falling_fruits.remove(fruit)

    def draw_fruits(self):
        for fruit in self.falling_fruits:
            fruit.draw(self.screen)

    def get_next_screen(self):
        if self.game_over and self.next_screen:
            return self.next_screen
        return None
