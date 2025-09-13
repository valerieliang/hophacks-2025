import pygame
import random
import math

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
STONE_RADIUS = 30
STEP_TOLERANCE = 50  # Max distance from stone center to count as a step
NUM_STEPS = 10

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GRAY = (180, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("River Crossing Minigame")
clock = pygame.time.Clock()

# Generate stepping stones
def generate_stones(num_steps):
    stones = []
    x = SCREEN_WIDTH // 4
    y = SCREEN_HEIGHT - 100
    side = 1
    for i in range(num_steps):
        stones.append((x, y))
        x += side * random.randint(120, 180)
        y -= random.randint(40, 70)
        side *= -1
    return stones

stones = generate_stones(NUM_STEPS)

# Simulated user feet positions (replace with real tracking in production)
def get_user_feet(step_idx):
    # Simulate user stepping on the stone, with some random error
    cx, cy = stones[step_idx]
    if random.random() < 0.2:  # 20% chance to "splash"
        offset = random.randint(STEP_TOLERANCE + 10, STEP_TOLERANCE + 40)
        angle = random.uniform(0, 2 * math.pi)
        fx = cx + offset * math.cos(angle)
        fy = cy + offset * math.sin(angle)
    else:
        fx = cx + random.randint(-10, 10)
        fy = cy + random.randint(-10, 10)
    # Simulate two feet
    return [(fx - 15, fy), (fx + 15, fy)]

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def main():
    running = True
    step_idx = 0
    splashes = 0
    completed = False

    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw stones
        for i, (x, y) in enumerate(stones):
            color = GRAY if i > step_idx else GREEN
            pygame.draw.circle(screen, color, (int(x), int(y)), STONE_RADIUS)

        if not completed:
            # Get user feet positions (simulate)
            feet = get_user_feet(step_idx)
            for fx, fy in feet:
                pygame.draw.circle(screen, BLUE, (int(fx), int(fy)), 12)

            # Check if both feet are close enough to the current stone
            cx, cy = stones[step_idx]
            if all(distance((fx, fy), (cx, cy)) < STEP_TOLERANCE for fx, fy in feet):
                step_idx += 1
            else:
                # Splash!
                splashes += 1
                pygame.draw.circle(screen, RED, (int(cx), int(cy)), STONE_RADIUS + 10, 4)
                step_idx += 1  # Still move forward

            if step_idx >= NUM_STEPS:
                completed = True

        # Show splash count and completion
        font = pygame.font.SysFont(None, 36)
        splash_text = font.render(f"Splashes: {splashes}", True, RED)
        screen.blit(splash_text, (10, 10))
        if completed:
            msg = font.render("River crossed!", True, GREEN)
            screen.blit(msg, (SCREEN_WIDTH // 2 - 100, 50))

        pygame.display.flip()
        pygame.time.wait(700)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()