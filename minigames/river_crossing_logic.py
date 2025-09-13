import numpy as np
import cv2
import random
import pygame

POINT_RADIUS = 40
MAX_X_DISTANCE = 150  # max horizontal distance a foot can reach from previous stone

class RiverCrossingGame:
    def __init__(self, points_to_win=5):
        self.score = 0
        self.game_over = False
        self.points_to_win = points_to_win
        self.stones = []  # dynamic stones
        self.generate_initial_stones()

    def generate_initial_stones(self):
        """Generate stones within reachable distance from left/right start."""
        start_x = 200
        y = 400  # placeholder, will be updated dynamically to match ankle height
        self.stones = [(start_x + i * MAX_X_DISTANCE, y) for i in range(self.points_to_win)]
        self.visited = [False] * len(self.stones)

    def update_stone_y(self, ankle_y):
        """Align all stones on same y-axis as the player's ankles."""
        self.stones = [(x, ankle_y) for x, _ in self.stones]

    def draw_stones(self, frame):
        """Draw only the next stone the player needs to step on"""
        try:
            next_index = self.visited.index(False)  # first unvisited stone
            x, y = self.stones[next_index]
            cv2.circle(frame, (x, y), POINT_RADIUS, (0, 0, 255), 3)
        except ValueError:
            # All stones visited
            pass


    def feet_positions(self, keypoints):
        if keypoints.shape[0] <= 16:
            return None
        left_ankle = keypoints[15][:2]
        right_ankle = keypoints[16][:2]
        return [tuple(map(int, left_ankle)), tuple(map(int, right_ankle))]

    def check_stones(self, feet):
        for i, (stone_x, stone_y) in enumerate(self.stones):
            if not self.visited[i]:
                for foot_x, foot_y in feet:
                    # threshold distance for scoring
                    if abs(foot_x - stone_x) < POINT_RADIUS and abs(foot_y - stone_y) < POINT_RADIUS:
                        self.visited[i] = True
                        self.score += 1
                        print(f"Scored! Total: {self.score}")
                        if self.score >= self.points_to_win:
                            self.game_over = True
                        break

    def update(self, keypoints_list):
        if self.game_over or keypoints_list is None:
            return

        for kp in keypoints_list:
            feet = self.feet_positions(kp)
            if feet is None:
                continue
            avg_ankle_y = sum(f[1] for f in feet) // len(feet)
            # update the stone's y-coordinate to match player's ankle
            next_index = self.visited.index(False)
            x, _ = self.stones[next_index]
            self.stones[next_index] = (x, avg_ankle_y)
            self.check_stones(feet)

    def update_stone_y(self, ankle_y):
        try:
            next_index = self.visited.index(False)
            x, _ = self.stones[next_index]
            self.stones[next_index] = (x, ankle_y)
        except ValueError:
            pass

    def draw_stone_on_surface(self, surface, offset=(0,0)):
        try:
            next_index = self.visited.index(False)
            x, y = self.stones[next_index]
            ox, oy = offset
            pygame.draw.circle(surface, (0,0,255), (x+ox, y+oy), POINT_RADIUS, 3)
        except ValueError:
            pass
