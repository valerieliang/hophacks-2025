import pygame
import cv2
import numpy as np
import threading
import time
import os
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button   # generic button
from assets.fonts import dynapuff

class TreePoseCamera:
    def __init__(self):
        pass