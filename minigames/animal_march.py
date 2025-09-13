# minigames/animal_march.py

import cv2
from ultralytics import YOLO
import numpy as np
import time

# Constants
KNEE_LIFT_THRESHOLD = 0.9  # Ratio of knee y to hip y (lower is higher knee)
STEP_SCORE_TARGET = 10     # Number of steps to finish minigame

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')  # Make sure you have this model

def get_keypoint(kps, idx):
    if kps is None or len(kps) <= idx * 3 + 2:
        return None
    return kps[idx*3], kps[idx*3+1], kps[idx*3+2]

def is_knee_lifted(kps, side='left'):
    if side == 'left':
        hip = get_keypoint(kps, 11)
        knee = get_keypoint(kps, 13)
    else:
        hip = get_keypoint(kps, 12)
        knee = get_keypoint(kps, 14)
    if hip is None or knee is None or hip[2] < 0.5 or knee[2] < 0.5:
        return False
    return knee[1] <= hip[1]

def update_score(kps, last_step, score, cooldown=0.3):
    """Check for alternating steps and return updated score and last_step."""
    import time
    now = time.time()
    left_lifted = is_knee_lifted(kps, 'left')
    right_lifted = is_knee_lifted(kps, 'right')

    new_last_step = last_step
    new_score = score
    if left_lifted and last_step != 'left':
        new_score += 1
        new_last_step = 'left'
        last_step_time = now
    elif right_lifted and last_step != 'right':
        new_score += 1
        new_last_step = 'right'
        last_step_time = now

    return new_score, new_last_step
