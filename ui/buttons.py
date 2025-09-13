import pygame

class Button:
    def __init__(self, screen, text="", font=None, font_size=48,
                 text_color=(255,255,255), bg_color=(0,0,0),
                 image=None, pos=(0,0), size=None):
        self.screen = screen
        self.text = text
        self.font = pygame.font.Font(font, font_size) if text else None
        self.text_color = text_color
        self.bg_color = bg_color
        self.image = None

        if image:
            loaded = pygame.image.load(image).convert_alpha()
            if size:
                loaded = pygame.transform.smoothscale(loaded, size)
            self.image = loaded
            self.rect = self.image.get_rect(center=pos)
        else:
            self.image = pygame.Surface(size)
            self.image.fill(bg_color)
            self.rect = self.image.get_rect(center=pos)

            if text:
                text_surface = self.font.render(text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                self.image.blit(text_surface, (self.rect.width//2 - text_rect.width//2,
                                               self.rect.height//2 - text_rect.height//2))

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
