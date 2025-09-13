import cv2
import pygame
import numpy as np
from pose_estimator import PoseEstimator

def init_camera_and_window(screen):
    screen_width, screen_height = screen.get_size()

    # open webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Failed to open camera")

    # detect pose
    annotated_frame, _ = PoseEstimator().detect(frame)
    frame_height, frame_width = annotated_frame.shape[:2]

    # calculate scale to fit screen while maintaining aspect ratio
    screen_ratio = screen_width / screen_height
    frame_ratio = frame_width / frame_height

    if frame_ratio > screen_ratio:
        # frame is wider than screen: fit width
        new_width = screen_width
        new_height = int(screen_width / frame_ratio)
    else:
        # frame is taller than screen: fit height
        new_height = screen_height
        new_width = int(screen_height * frame_ratio)

    # resize
    frame_resized = cv2.resize(annotated_frame, (new_width, new_height))
    frame_resized = cv2.flip(frame_resized, 1)

    # convert to PyGame surface
    frame_surface = pygame.surfarray.make_surface(np.rot90(frame_resized))

    # center frame on screen
    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2
    screen.blit(frame_surface, (x_offset, y_offset))
    pygame.display.update()

    return cap
