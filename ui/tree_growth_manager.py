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
        self.growth_speed = 0.33  # faster growth
        self.countdown_finished = False  # to stop growth once countdown ends

    def start_new_tree(self):
        """Start growing a new random tree on left or right edge"""
        # Only start a new tree if none active
        if self.active:
            return

        self.current_tree = random.choice(self.tree_images)
        
        # Choose left or right edge
        side = random.choice(["left", "right"])
        x = 0 if side == "left" else self.screen_w - self.current_tree.get_width()

        y = self.screen_h  # bottom aligned
        self.current_pos = (x, y)
        self.progress = 0.0
        self.active = True
        self.finished = False
        self.countdown_finished = False

    def update(self, seconds_left, hold_time):
        """Update growth based on countdown"""
        if not self.active or self.finished:
            return

        if seconds_left is not None and seconds_left > 0:
            # Grow tree proportionally plus speed
            self.progress = min(1.0, 1.0 - (seconds_left / hold_time) + self.growth_speed)
        else:
            # Stop growth once countdown ends
            self.countdown_finished = True

        if self.progress >= 1.0 or self.countdown_finished:
            self.progress = min(1.0, self.progress)
            self.finished = True

    def draw(self, screen):
        if not self.active or self.current_tree is None:
            return

        # Original size
        tree_w, tree_h = self.current_tree.get_size()

        # Height goes from 0.5 * screen_h → 1.0 * screen_h
        min_h = int(self.screen_h * 0.5)
        max_h = self.screen_h
        new_h = int(min_h + (max_h - min_h) * self.progress)

        # Make tree skinnier: scale width to 50%-70% of original
        skinny_factor = 0.3 
        new_w = int(tree_w * skinny_factor)

        # Scale the tree
        scaled_tree = pygame.transform.smoothscale(self.current_tree, (new_w, new_h))

        # Align bottom
        x, y_bottom = self.current_pos
        # If tree is on the right, adjust x so it still touches the edge
        if x > 0:
            x = self.screen_w - new_w
        y_top = y_bottom - new_h
        screen.blit(scaled_tree, (x, y_top))


    def reset(self):
        self.active = False
        self.current_tree = None
        self.progress = 0.0
        self.finished = False
        self.countdown_finished = False
