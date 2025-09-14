import numpy as np
import pygame
import random
from collections import deque

POINT_RADIUS = 60  # Increased from 40 for easier targeting
STONE_DETECTION_RADIUS = 80  # Even more generous detection area
MIN_STONE_DISTANCE = 100  # Minimum distance from current foot position
MAX_STONE_DISTANCE = 300  # Maximum distance from current foot position

class RiverCrossingGame:
    def __init__(self, points_to_win=5):
        self.score = 0
        self.game_over = False
        self.points_to_win = points_to_win
        self.current_stone = None
        self.screen_width = 1280  # Default screen width, can be updated
        self.screen_height = 720  # Default screen height, can be updated
        
        # Foot position smoothing
        self.foot_history_len = 5
        self.left_foot_history = deque(maxlen=self.foot_history_len)
        self.right_foot_history = deque(maxlen=self.foot_history_len)
        
        # Stone hit detection
        self.hit_cooldown = 0
        self.min_cooldown_frames = 30  # Prevent multiple hits on same stone
        
        # Track current foot positions for stone generation
        self.current_foot_positions = []
        self.last_foot_y = None

    def set_screen_dimensions(self, width, height):
        """Update screen dimensions for stone placement"""
        self.screen_width = width
        self.screen_height = height

    def feet_positions(self, keypoints, conf_threshold=0.5):
        """
        keypoints: list of 17 [x,y,conf]
        Returns list of detected ankles [(x,y), ...] or None if none found
        """
        if keypoints is None or len(keypoints) < 17:
            return None

        # Extract ankle keypoints (indices 15 and 16)
        left_ankle = keypoints[15]   # [x, y, conf]
        right_ankle = keypoints[16]  # [x, y, conf]
        
        left_x, left_y, left_conf = left_ankle
        right_x, right_y, right_conf = right_ankle

        feet = []
        
        # Check left ankle
        if left_conf >= conf_threshold:
            # Add to smoothing history
            self.left_foot_history.append((left_x, left_y))
            if len(self.left_foot_history) >= 3:
                # Use smoothed position
                avg_x = sum(pos[0] for pos in self.left_foot_history) / len(self.left_foot_history)
                avg_y = sum(pos[1] for pos in self.left_foot_history) / len(self.left_foot_history)
                feet.append((int(avg_x), int(avg_y)))
            else:
                feet.append((int(left_x), int(left_y)))
        
        # Check right ankle  
        if right_conf >= conf_threshold:
            # Add to smoothing history
            self.right_foot_history.append((right_x, right_y))
            if len(self.right_foot_history) >= 3:
                # Use smoothed position
                avg_x = sum(pos[0] for pos in self.right_foot_history) / len(self.right_foot_history)
                avg_y = sum(pos[1] for pos in self.right_foot_history) / len(self.right_foot_history)
                feet.append((int(avg_x), int(avg_y)))
            else:
                feet.append((int(right_x), int(right_y)))

        return feet if feet else None

    def generate_next_stone(self, current_feet):
        """Generate a random stone position that's reachable from current foot positions"""
        if not current_feet:
            # If no feet detected, place stone in center of screen
            stone_x = self.screen_width // 2
            stone_y = self.screen_height // 2
        else:
            # Get average foot position
            avg_x = sum(f[0] for f in current_feet) / len(current_feet)
            avg_y = sum(f[1] for f in current_feet) / len(current_feet)
            
            # Store the Y level for consistent stone placement
            self.last_foot_y = avg_y
            
            # Generate random position within reachable distance
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(MIN_STONE_DISTANCE, MAX_STONE_DISTANCE)
            
            stone_x = int(avg_x + distance * np.cos(angle))
            stone_y = int(avg_y + distance * np.sin(angle) * 0.3)  # Reduce Y variation
            
            # Keep stone within screen bounds with padding
            padding = POINT_RADIUS + 10
            stone_x = max(padding, min(self.screen_width - padding, stone_x))
            stone_y = max(padding, min(self.screen_height - padding, stone_y))
        
        self.current_stone = (stone_x, stone_y)

    def update(self, keypoints_list):
        if self.game_over or not keypoints_list:
            return

        # Reduce hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # Get current foot positions
        current_feet = []
        for kp in keypoints_list:
            feet = self.feet_positions(kp)
            if feet:
                current_feet.extend(feet)
                break  # Use first valid detection
        
        self.current_foot_positions = current_feet
        
        # Generate first stone if none exists
        if self.current_stone is None:
            self.generate_next_stone(current_feet)
            return
        
        # Check for stone hits
        if current_feet:
            self.check_stones(current_feet)

    def check_stones(self, feet):
        """Check if any foot is touching the current stone"""
        if self.hit_cooldown > 0 or self.current_stone is None:
            return
            
        stone_x, stone_y = self.current_stone
        
        # Check each foot against the stone
        for foot_x, foot_y in feet:
            distance = np.sqrt((foot_x - stone_x)**2 + (foot_y - stone_y)**2)
            
            # Very generous detection - use the larger detection radius
            if distance <= STONE_DETECTION_RADIUS:
                # Stone hit!
                self.score += 1
                self.hit_cooldown = self.min_cooldown_frames
                
                # Check if game is complete
                if self.score >= self.points_to_win:
                    self.game_over = True
                    self.current_stone = None
                else:
                    # Generate next stone
                    self.generate_next_stone(feet)
                
                return  # Exit after first hit

    def draw_stone_on_surface(self, surface, offset=(0,0)):
        """Draw the current stone that needs to be reached"""
        if self.current_stone is None:
            return
            
        stone_x, stone_y = self.current_stone
        ox, oy = offset
        
        # Draw the stone as a blue circle with a border
        pygame.draw.circle(surface, (0, 150, 255), (stone_x + ox, stone_y + oy), POINT_RADIUS, 0)
        pygame.draw.circle(surface, (0, 100, 200), (stone_x + ox, stone_y + oy), POINT_RADIUS, 3)
        
        # Draw detection area (optional - for debugging)
        # pygame.draw.circle(surface, (100, 200, 255, 50), (stone_x + ox, stone_y + oy), STONE_DETECTION_RADIUS, 2)
        
        # Draw stone number (current score + 1)
        font = pygame.font.Font(None, 48)
        text = font.render(str(self.score + 1), True, (255, 255, 255))
        text_rect = text.get_rect(center=(stone_x + ox, stone_y + oy))
        surface.blit(text, text_rect)
        
        # Draw progress indicator
        progress_text = f"Stone {self.score + 1}/{self.points_to_win}"
        progress_font = pygame.font.Font(None, 36)
        progress_surface = progress_font.render(progress_text, True, (255, 255, 255))
        surface.blit(progress_surface, (10, 10))

    def draw_foot_positions(self, surface, offset=(0,0)):
        """Helper method to draw current foot positions for debugging"""
        ox, oy = offset
        for i, (fx, fy) in enumerate(self.current_foot_positions):
            color = (255, 100, 100) if i == 0 else (100, 255, 100)  # Red for left, green for right
            pygame.draw.circle(surface, color, (fx + ox, fy + oy), 15, 3)

    def reset_game(self):
        """Reset the game state for a new round"""
        self.score = 0
        self.game_over = False
        self.current_stone = None
        self.hit_cooldown = 0
        self.left_foot_history.clear()
        self.right_foot_history.clear()
        self.current_foot_positions = []
        self.last_foot_y = None