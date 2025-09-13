import pygame

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()

        # Load background
        self.background = pygame.image.load("assets/homepage_background.jpg").convert()
        self.background = pygame.transform.scale(self.background, (w, h))

        # Load logo
        self.logo = pygame.image.load("assets/logo.png").convert_alpha()
        logo_w = int(w * 0.75)  # scale to ~75% of screen width
        logo_h = int(self.logo.get_height() * (logo_w / self.logo.get_width()))
        self.logo = pygame.transform.scale(self.logo, (logo_w, logo_h))
        self.logo_rect = self.logo.get_rect(center=(w // 2, h // 2 - 100))

        # Load start button
        self.start_button = pygame.image.load("assets/start_game.png").convert_alpha()
        button_w = int(w * 0.5)
        button_h = int(self.start_button.get_height() * (button_w / self.start_button.get_width()))
        self.start_button = pygame.transform.scale(self.start_button, (button_w, button_h))
        self.start_button_rect = self.start_button.get_rect(center=(w // 2, h // 2 + 200))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.logo, self.logo_rect)
        self.screen.blit(self.start_button, self.start_button_rect)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(mouse_pos):
                return "stage_select"  # go to stage select when clicked
        return None
