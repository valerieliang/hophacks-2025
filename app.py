import cv2
import pygame
import sys
from pose_estimator import PoseEstimator
import numpy as np

# Initialize PyGame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pose Tracking")

# Fonts & colors
font = pygame.font.SysFont("Arial", 28)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 200, 100)
BUTTON_HOVER = (150, 255, 150)

# Pose estimator
pose_estimator = PoseEstimator()

# Camera flag
camera_on = False
cap = None

# Button setup
button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60)

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    # Draw button
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)
    text_surface = font.render("Start Camera" if not camera_on else "Camera Running", True, BLACK)
    screen.blit(text_surface, (button_rect.x + 20, button_rect.y + 15))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos) and not camera_on:
                cap = cv2.VideoCapture(0)
                camera_on = True

    # Camera frame
    if camera_on and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            annotated_frame, keypoints = pose_estimator.detect(frame)
            # Convert OpenCV BGR -> RGB for PyGame
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            annotated_frame = np.rot90(annotated_frame)
            frame_surface = pygame.surfarray.make_surface(annotated_frame)
            screen.blit(frame_surface, (0, 0))

    pygame.display.update()
    clock.tick(30)

# Cleanup
if cap:
    cap.release()
pygame.quit()
sys.exit()
