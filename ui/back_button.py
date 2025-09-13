import pygame

class BackButton:
    def __init__(self, screen, image_path=None, pos=(50, 50), size=(80, 50), text="Back"):
        """
        image_path: optional path to an icon; if None, draw rectangle + text
        pos: center position
        size: width, height
        """
        self.screen = screen
        self.size = size
        self.pos = pos

        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, size)
            self.rect = self.image.get_rect(center=pos)
            self.use_image = True
        else:
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.rect = pygame.Rect(0, 0, size[0], size[1])
            self.rect.center = pos
            self.use_image = False

    def draw(self):
        if self.use_image:
            self.screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), self.rect, border_radius=8)
            text_surf = self.font.render("Back", True, (255, 255, 255))
            self.screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
