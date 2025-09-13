import pygame

IMAGE_PATH = "assets/back_button.png"
POSITION = (60, 60)  # default position
SIZE = (64, 64)  # default size

class BackButton:
    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load(IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, SIZE)
        self.rect = self.image.get_rect(center=POSITION)

    def draw(self):
        # Always draw on top layer
        self.screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
