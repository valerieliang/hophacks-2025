import pygame
import sys

# Example wrist and leg point data (replace with real tracking data)
# Each tuple: (frame_number, wrist_y, leg_y)
movement_data = [
    (0, 100, 300),
    (1, 110, 310),
    (2, 90, 290),
    (3, 120, 320),
    (4, 80, 280),
    (5, 130, 330),
    (6, 70, 270),
    (7, 140, 340),
]
def detect_steps(data):
    points = 0
    last_wrist_dir = 0
    last_leg_dir = 0
    for i in range(1, len(data)):
        _, wrist_y_prev, leg_y_prev = data[i-1]
        _, wrist_y, leg_y = data[i]
        wrist_dir = 1 if wrist_y > wrist_y_prev else -1
        leg_dir = 1 if leg_y > leg_y_prev else -1
        # Detect alternation (direction change)
        if wrist_dir != last_wrist_dir and leg_dir != last_leg_dir:
            points += 1
        last_wrist_dir = wrist_dir
        last_leg_dir = leg_dir
    return points

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Fruit Points")
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()

    # Simulate step detection
    points = detect_steps(movement_data)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        # Display points in top right
        points_text = font.render(f"Points: {points}", True, (0, 0, 0))
        text_rect = points_text.get_rect(topright=(630, 10))
        screen.blit(points_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()