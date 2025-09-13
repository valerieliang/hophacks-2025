import pygame
import os

IMAGE_PATH = "assets/back_button.png"
POSITION = (60, 60)
SIZE = (64, 64)

class BackButton:
    def __init__(self, screen, image_path=IMAGE_PATH, pos=POSITION, size=SIZE):
        self.screen = screen

        # Check if image exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Back button image not found: {image_path}")

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=pos)

    def draw(self):
        # Make sure this is drawn *after* all background and other elements
        self.screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
