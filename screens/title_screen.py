import pygame
from ui.buttons import Button

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 96, bold=True)

        self.play_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 150),
            size=(200, 80),
            text="Play"
        )

    def draw(self):
        self.screen.fill((0, 0, 0))
        title = self.title_font.render("MoveQuest", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width()//2, 200)))
        self.play_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.play_button.is_clicked(mouse_pos):
            return "jungle_intro"
        return None
