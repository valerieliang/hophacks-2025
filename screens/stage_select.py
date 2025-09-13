import pygame
from ui.buttons import Button

class StageSelect:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        w, h = screen.get_size()

        # Buttons: Jungle + placeholders
        self.jungle_button = Button(
            screen,
            image=None,
            pos=(w // 2, 200),
            size=(400, 100),
            text="🌴 Jungle Adventure"
        )

        self.placeholder1 = Button(
            screen,
            image=None,
            pos=(w // 2, 350),
            size=(400, 100),
            text="[PLACEHOLDER]"
        )

        self.placeholder2 = Button(
            screen,
            image=None,
            pos=(w // 2, 500),
            size=(400, 100),
            text="[PLACEHOLDER]"
        )

    def draw(self):
        self.screen.fill((30, 30, 80))
        title = self.font.render("Select a Stage", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 80)))

        self.jungle_button.draw()
        self.placeholder1.draw()
        self.placeholder2.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.jungle_button.is_clicked(mouse_pos):
                return "jungle_intro"
            if self.placeholder1.is_clicked(mouse_pos) or self.placeholder2.is_clicked(mouse_pos):
                print("Placeholder stage clicked.")
        return None
