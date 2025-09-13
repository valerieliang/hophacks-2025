import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from assets.fonts import dynapuff

class JungleSelector:
    def __init__(self, screen):
        self.screen = screen
        self.font = dynapuff(36, bold=True)
        self.small_font = dynapuff(24)
        self.back_button = BackButton(screen)

        w, h = screen.get_size()

        self.animal_march_button = Button(
            screen,
            image=None,
            pos=(w // 2, 200),
            size=(400, 70),
            text="Animal March"
        )

        # place holders for other stages
        self.placeholder1 = pygame.Rect(w//2 - 200, 300, 400, 70)
        self.placeholder2 = pygame.Rect(w//2 - 200, 400, 400, 70)
        self.placeholder_color = (100, 100, 100)
        
    def draw(self):
        self.screen.fill((60, 120, 60))
        title = self.font.render("Select a Mini-Game", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width()//2, 60)))
        
        # draw buttons
        self.animal_march_button.draw()
        pygame.draw.rect(self.screen, self.placeholder_color, self.placeholder1, border_radius=12)
        pygame.draw.rect(self.screen, self.placeholder_color, self.placeholder2, border_radius=12)        
        
        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_intro"
            if self.animal_march_button.is_clicked(mouse_pos):
                return "animal_march_intro"
        return None
