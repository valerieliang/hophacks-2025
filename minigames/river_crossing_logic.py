import numpy as np
import pygame

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

    def feet_positions(self, keypoints, conf_threshold=0.3):
        """
        keypoints: list of 17 [x,y,conf]
        Returns list of detected ankles [(x,y), ...] or None if none found
        """
        if keypoints is None or len(keypoints) < 17:
            print(f"Partial keypoints detected: {0 if keypoints is None else len(keypoints)} points")
            return None

        left_x, left_y, left_conf = keypoints[15]
        right_x, right_y, right_conf = keypoints[16]

        feet = []
        if left_conf >= conf_threshold:
            feet.append((int(left_x), int(left_y)))
        if right_conf >= conf_threshold:
            feet.append((int(right_x), int(right_y)))

        if len(feet) == 2:
            print(f"Both ankles detected: L({left_x},{left_y},{left_conf}), R({right_x},{right_y},{right_conf})")
        elif len(feet) == 1:
            missing = "Left" if left_conf < conf_threshold else "Right"
            print(f"Only one ankle detected ({missing} missing): {feet[0]}")
        else:
            print(f"No ankles detected with sufficient confidence: L:{left_conf} R:{right_conf}")
            return None

        return feet


    def update(self, keypoints_list):
        if self.game_over or not keypoints_list:
            return

        # Generate first stones if not yet
        if self.score == 0 and not self.stones_generated:
            for kp in keypoints_list:
                feet = self.feet_positions(kp)
                if feet:
                    avg_y = sum(f[1] for f in feet) // len(feet)
                    start_x = 200
                    self.stones = [(start_x + i * MAX_X_DISTANCE, avg_y) for i in range(self.points_to_win)]
                    self.visited = [False] * len(self.stones)
                    self.stones_generated = True
                    print(f"Initial stones generated at Y={avg_y}, feet={feet}")
                    break

        # Update stones & scoring
        for kp in keypoints_list:
            feet = self.feet_positions(kp)
            if not feet:
                continue

            try:
                next_index = self.visited.index(False)
                x, _ = self.stones[next_index]
                avg_y = sum(f[1] for f in feet) // len(feet)
                self.stones[next_index] = (x, avg_y)
                self.check_stones(feet)
            except ValueError:
                pass  # all stones visited


    def check_stones(self, feet):
        for i, (stone_x, stone_y) in enumerate(self.stones):
            if not self.visited[i]:
                for fx, fy in feet:
                    if abs(fx - stone_x) < POINT_RADIUS and abs(fy - stone_y) < POINT_RADIUS:
                        self.visited[i] = True
                        self.score += 1
                        print(f"Scored! Total: {self.score}")
                        if self.score >= self.points_to_win:
                            self.game_over = True
                        break

    def draw_stone_on_surface(self, surface, offset=(0,0)):
        try:
            next_index = self.visited.index(False)
            x, y = self.stones[next_index]
            ox, oy = offset
            pygame.draw.circle(surface, (0,0,255), (x+ox, y+oy), POINT_RADIUS, 3)
        except ValueError:
            pass  # all stones visited
