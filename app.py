import pygame
import sys
import numpy as np
import cv2
from pose_estimator import PoseEstimator
from ui.frame_manager import init_camera_and_window
from ui.camera_toggle import CameraToggleButton

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
                    # turn camera ON
                    cap = init_camera_and_window(screen)
                    camera_on = True
                    toggle_button.rect.midbottom = (screen.get_width() // 2, screen.get_height() - 20)
                else:
                    # turn camera OFF
                    if cap:
                        cap.release()
                    camera_on = False
                    # keep screen size same
                    toggle_button.rect.midbottom = (screen.get_width() // 2, screen.get_height() - 20)

    # camera frame
    if camera_on and cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            annotated_frame, keypoints = pose_estimator.detect(frame)
            frame_height, frame_width = annotated_frame.shape[:2]

            # calculate aspect ratio scaling
            screen_ratio = screen.get_width() / screen.get_height()
            frame_ratio = frame_width / frame_height

            if frame_ratio > screen_ratio:
                # fit width
                new_width = screen.get_width()
                new_height = int(screen.get_width() / frame_ratio)
            else:
                # fit height
                new_height = screen.get_height()
                new_width = int(screen.get_height() * frame_ratio)

            # resize and mirror
            frame_resized = cv2.resize(annotated_frame, (new_width, new_height))
            frame_resized = cv2.flip(frame_resized, 1)

            # convert to PyGame surface
            frame_surface = pygame.surfarray.make_surface(np.rot90(frame_resized))

            # center frame
            x_offset = (screen.get_width() - new_width) // 2
            y_offset = (screen.get_height() - new_height) // 2
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
