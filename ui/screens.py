import pygame
from ui.buttons import Button

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.font = pygame.font.SysFont("Arial", 96, bold=True)

        # Title text surface
        self.title_surface = self.font.render("MoveQuest", True, (50, 100, 200))
        self.title_rect = self.title_surface.get_rect(center=(w//2, h//3))

        # Play button
        self.play_button = Button(
            screen, text="Play", font_size=64,
            text_color=(255,255,255), bg_color=(0,200,0),
            pos=(w//2, h//2), size=(200, 80)
        )

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.screen.blit(self.title_surface, self.title_rect)
        self.play_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.is_clicked(mouse_pos):
                return "stage_select"
        return None


class StageSelectScreen:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.font = pygame.font.SysFont("Arial", 48)

        self.header = self.font.render("Choose a stage:", True, (255,255,255))
        self.header_rect = self.header.get_rect(midtop=(w//2, 50))

        # Stage buttons
        self.stage_buttons = []
        for i in range(1, 6):
            btn = Button(
                screen, text=f"Stage {i}",
                font_size=36, text_color=(0,0,0), bg_color=(200,200,200),
                pos=(w//2, 150 + i*80), size=(300, 60)
            )
            self.stage_buttons.append(btn)

    def draw(self):
        self.screen.fill((50, 50, 50))
        self.screen.blit(self.header, self.header_rect)
        for btn in self.stage_buttons:
            btn.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, btn in enumerate(self.stage_buttons, start=1):
                if btn.is_clicked(mouse_pos):
                    return f"stage_{i}"
        return None
