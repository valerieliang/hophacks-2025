import pygame
from ui.buttons import Button
from ui.back_button import BackButton

class JungleSelector:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.back_button = BackButton(screen, pos=(60, 60))

        w, h = screen.get_size()
        self.stage_buttons = []
        stage_names = [
            "Animal March", "Tree Pose Challenge",
            "Monkey Moves", "Jungle Explorer",
            "River Crossing", "Coconut Catch", "Jungle Rest"
        ]
        for i, name in enumerate(stage_names):
            btn = Button(
                screen,
                image=None,
                pos=(w // 2, 150 + i*100),
                size=(400, 70),
                text=name
            )
            self.stage_buttons.append(btn)

    def draw(self):
        self.screen.fill((60, 120, 60))
        title = self.font.render("Choose a Jungle Mini-Game", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width()//2, 60)))

        for btn in self.stage_buttons:
            btn.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.stage_buttons:
                if btn.is_clicked(mouse_pos):
                    return "jungle_stage"
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_intro"
        return None
