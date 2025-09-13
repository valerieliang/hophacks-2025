import pygame

BUTTON_DIM = 300  # button width and height
Y_OFFSET = 20  # distance from bottom of screen
IMAGE_PATH = "assets/camera_button.png"

class CameraToggleButton:

    def __init__(self, screen):
        self.screen = screen
        self.original_image = pygame.image.load(IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.smoothscale(self.original_image, (BUTTON_DIM, BUTTON_DIM))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (screen.get_width() // 2, screen.get_height() - 20)

        self.rect = self.image.get_rect()
        # center horizontally, y_offset from bottom
        self.rect.midbottom = (screen.get_width() // 2, screen.get_height() - Y_OFFSET)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
