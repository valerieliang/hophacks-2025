import numpy as np
import pygame
from collections import deque

POINT_RADIUS = 40
MAX_X_DISTANCE = 150  # max horizontal distance a foot can reach from previous stone

class RiverCrossingGame:
    def __init__(self, points_to_win=5):
        self.score = 0
        self.game_over = False
        self.points_to_win = points_to_win
        self.stones = []
        self.visited = []
        self.stones_generated = False  # only generate initial stones once
        
        # Foot position smoothing
        self.foot_history_len = 5
        self.left_foot_history = deque(maxlen=self.foot_history_len)
        self.right_foot_history = deque(maxlen=self.foot_history_len)
        
        # Stone hit detection
        self.hit_cooldown = 0
        self.min_cooldown_frames = 30  # Prevent multiple hits on same stone

    def feet_positions(self, keypoints, conf_threshold=0.5):
        """
        keypoints: list of 17 [x,y,conf]
        Returns list of detected ankles [(x,y), ...] or None if none found
        """
        if keypoints is None or len(keypoints) < 17:
            print(f"Partial keypoints detected: {0 if keypoints is None else len(keypoints)} points")
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

        # Debug output
        if len(feet) == 2:
            print(f"Both ankles detected: L({left_x:.1f},{left_y:.1f},{left_conf:.2f}), R({right_x:.1f},{right_y:.1f},{right_conf:.2f})")
        elif len(feet) == 1:
            missing = "Right" if left_conf >= conf_threshold else "Left"
            detected = "Left" if left_conf >= conf_threshold else "Right"
            print(f"Only {detected} ankle detected ({missing} missing): {feet[0]}")
        else:
            print(f"No ankles detected with sufficient confidence: L:{left_conf:.2f} R:{right_conf:.2f}")
            return None

        return feet

    def update(self, keypoints_list):
        if self.game_over or not keypoints_list:
            return

        # Reduce hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # Generate stones ONLY ONCE when not yet generated
        if not self.stones_generated:
            for kp in keypoints_list:
                feet = self.feet_positions(kp)
                if feet and len(feet) >= 1:
                    # Use the average Y position of detected feet
                    avg_y = sum(f[1] for f in feet) // len(feet)
                    
                    # Generate stones in a line across the screen - PERMANENTLY FIXED POSITIONS
                    start_x = 200
                    self.stones = []
                    for i in range(self.points_to_win):
                        stone_x = start_x + i * MAX_X_DISTANCE
                        self.stones.append((stone_x, avg_y))
                    
                    self.visited = [False] * len(self.stones)
                    self.stones_generated = True  # SET FLAG TO NEVER GENERATE AGAIN
                    print(f"Stones PERMANENTLY generated at Y={avg_y}")
                    print(f"Stone positions LOCKED: {self.stones}")
                    break
            return  # Exit early if stones not generated yet

        # ONLY check for hits if stones are already generated (no stone modification)
        for kp in keypoints_list:
            feet = self.feet_positions(kp)
            if feet:
                self.check_stones(feet)

    def check_stones(self, feet):
        """Check if any foot is touching the next stone"""
        if self.hit_cooldown > 0:
            return
            
        try:
            # Find the next unvisited stone
            next_index = self.visited.index(False)
            stone_x, stone_y = self.stones[next_index]
            
            # Check each foot against the stone with more generous detection
            for i, (fx, fy) in enumerate(feet):
                distance_x = abs(fx - stone_x)
                distance_y = abs(fy - stone_y)
                
                # More generous detection - larger radius and separate X/Y thresholds
                hit_radius_x = POINT_RADIUS + 20  # Extra 20 pixels in X direction
                hit_radius_y = POINT_RADIUS + 15  # Extra 15 pixels in Y direction
                
                foot_name = "Left" if i == 0 else "Right"
                
                # Debug print for each foot
                print(f"{foot_name} foot: ({fx},{fy}) vs Stone: ({stone_x},{stone_y}) - X_diff: {distance_x:.1f}, Y_diff: {distance_y:.1f}")
                
                # Check if foot is within the generous detection area
                if distance_x <= hit_radius_x and distance_y <= hit_radius_y:
                    self.visited[next_index] = True
                    self.score += 1
                    self.hit_cooldown = self.min_cooldown_frames
                    
                    print(f"STONE HIT! {foot_name} foot hit stone {next_index + 1}")
                    print(f"Score: {self.score}/{self.points_to_win}")
                    
                    if self.score >= self.points_to_win:
                        self.game_over = True
                        print("Game completed!")
                    return  # Exit after first hit
                    
        except ValueError:
            # All stones have been visited
            pass

    def draw_stone_on_surface(self, surface, offset=(0,0)):
        """Draw the next stone that needs to be reached"""
        try:
            next_index = self.visited.index(False)
            stone_x, stone_y = self.stones[next_index]
            ox, oy = offset
            
            # Draw the stone as a blue circle
            pygame.draw.circle(surface, (0, 100, 255), (stone_x + ox, stone_y + oy), POINT_RADIUS, 5)
            
            # Draw stone number
            font = pygame.font.Font(None, 36)
            text = font.render(str(next_index + 1), True, (255, 255, 255))
            text_rect = text.get_rect(center=(stone_x + ox, stone_y + oy))
            surface.blit(text, text_rect)
            
            # Draw all future stones as smaller circles
            for i in range(next_index + 1, len(self.stones)):
                future_x, future_y = self.stones[i]
                pygame.draw.circle(surface, (150, 150, 255), (future_x + ox, future_y + oy), POINT_RADIUS // 2, 2)
                
        except ValueError:
            # All stones visited - could draw a completion indicator
            pass

    def reset_game(self):
        """Reset the game state for a new round"""
        self.score = 0
        self.game_over = False
        self.stones = []
        self.visited = []
        self.stones_generated = False
        self.hit_cooldown = 0
        self.left_foot_history.clear()
        self.right_foot_history.clear()
        print("Game reset")