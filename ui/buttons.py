import pygame

class Button:
    def __init__(self, screen, image=None, pos=(0,0), size=None, text=""):
        self.screen = screen
        self.image = None
        if image:
            self.image = pygame.image.load(image).convert_alpha()
            if size:
                self.image = pygame.transform.scale(self.image, size)
            self.rect = self.image.get_rect(center=pos)
        else:
            self.font = pygame.font.SysFont("Arial", 32)
            self.text = text
            self.rect = pygame.Rect(0, 0, size[0], size[1])
            self.rect.center = pos

    def draw(self):
        if self.image:
            self.screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(self.screen, (50, 150, 50), self.rect, border_radius=12)
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
