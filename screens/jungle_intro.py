import pygame
from ui.buttons import Button

class JungleIntro:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 28)

        # Load stage icon
        self.icon = pygame.image.load("assets/jungle_adventure_icon.png").convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (300, 300))  # adjust size as needed

        self.start_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 100),
            size=(260, 80),
            text="Choose Mini-Games"
        )

    def draw(self):
        self.screen.fill((34, 139, 34))

        title = self.title_font.render("Jungle Adventure Quest", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 100)))

        # Draw the stage icon in the middle
        self.screen.blit(self.icon, self.icon.get_rect(center=(self.screen.get_width() // 2, 300)))

        # Description under the image (for parents)
        desc_lines = [
            "In this stage, children practice coordination, balance,",
            "and gross motor skills through fun jungle-themed games.",
            "Each exercise is wrapped in a story to keep them engaged."
        ]
        for i, line in enumerate(desc_lines):
            text = self.desc_font.render(line, True, (240, 240, 240))
            self.screen.blit(text, text.get_rect(center=(self.screen.get_width() // 2, 500 + i * 40)))

        self.start_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.start_button.is_clicked(mouse_pos):
            return "jungle_selector"
        return None
