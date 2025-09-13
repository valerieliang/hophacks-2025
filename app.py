import pygame
import sys
import numpy as np
import cv2
from pose_estimator import PoseEstimator
from ui.frame_manager import init_camera_and_window
from ui.camera_toggle import CameraToggleButton
from ui.camera_manager import CameraManager


pygame.init()

# detect screen size for normal windowed mode
info = pygame.display.Info()
screen_width, screen_height = info.current_w - 50, info.current_h - 100
# square window
screen = pygame.display.set_mode((screen_height, screen_height))

WHITE = (255, 255, 255)
clock = pygame.time.Clock()

pose_estimator = PoseEstimator()

# camera variables
camera_on = False
cap = None
toggle_button = CameraToggleButton(screen)
camera_manager = CameraManager(screen)

running = True
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if toggle_button.is_clicked(mouse_pos):
                if not camera_on:
                    camera_manager.start_camera()
                    camera_on = True
                else:
                    camera_manager.stop_camera()
                    camera_on = False
    # camera frame
    if camera_on:
        result = camera_manager.get_frame_surface()
        if result:
            frame_surface, x_offset, y_offset = result
            screen.blit(frame_surface, (x_offset, y_offset))

    # draw camera toggle button on top
    toggle_button.draw()

    pygame.display.update()
    clock.tick(30)

# Cleanup
if cap:
    cap.release()
pygame.quit()
sys.exit()
