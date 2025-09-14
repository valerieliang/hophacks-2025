import pygame
import random

class TreeGrowthManager:
    def __init__(self, screen_size):
        self.screen_w, self.screen_h = screen_size
        self.tree_images = [
            pygame.image.load("assets/trees/tree_a.png").convert_alpha(),
            pygame.image.load("assets/trees/tree_b.png").convert_alpha(),
            pygame.image.load("assets/trees/tree_c.png").convert_alpha()
        ]
        self.current_tree = None
        self.current_pos = None
        self.progress = 0.0   # 0.0 = half height, 1.0 = full height
        self.active = False
        self.finished = False

    def start_new_tree(self):
        """Start growing a new random tree in a safe spot"""
        self.current_tree = random.choice(self.tree_images)
        
        # Pick random x, avoiding the human frame (middle of screen)
        safe_margin = 200
        mid_zone = (self.screen_w // 2 - safe_margin, self.screen_w // 2 + safe_margin)
        while True:
            x = random.randint(50, self.screen_w - 150)
            if not (mid_zone[0] <= x <= mid_zone[1]):
                break

        y = self.screen_h  # bottom aligned
        self.current_pos = (x, y)
        self.progress = 0.0
        self.active = True
        self.finished = False

    def update(self, seconds_left, hold_time):
        """Update growth based on countdown"""
        if not self.active:
            return

        if seconds_left is not None and seconds_left > 0:
            self.progress = 1.0 - (seconds_left / hold_time)
        else:
            # Ensure the tree finishes if countdown ends but game isn’t over yet
            self.progress = min(1.0, self.progress + 0.02)

        if self.progress >= 1.0:
            self.finished = True

    def draw(self, screen):
        if not self.active or self.current_tree is None:
            return

        # Keep width fixed
        tree_w, tree_h = self.current_tree.get_size()

        # Height goes from 0.5 * screen_h → 1.0 * screen_h
        min_h = int(self.screen_h * 0.5)
        max_h = self.screen_h
        new_h = int(min_h + (max_h - min_h) * self.progress)

        # Scale only vertically
        scaled_tree = pygame.transform.smoothscale(self.current_tree, (tree_w, new_h))

        # Align bottom
        x, y_bottom = self.current_pos
        y_top = y_bottom - new_h
        screen.blit(scaled_tree, (x, y_top))

    def reset(self):
        self.active = False
        self.current_tree = None
        self.progress = 0.0
        self.finished = False
