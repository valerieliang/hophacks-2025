import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from assets.fonts import dynapuff

class AnimalMarchIntro:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()

        # Title font for kids
        self.title_font = dynapuff(64, bold=True) 
        # Description font for parents
        self.desc_font = dynapuff(24)

        # Start button to toggle camera
        self.start_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 100),
            size=(220, 70),
            text="Start Exercise"
        )

        # Back button
        self.back_button = BackButton(screen, pos=(60, 60))

    def draw(self):
        self.screen.fill((102, 204, 255))  # bright, fun blue background

        # Kid-friendly title / intro
        title_text = "Animal March"
        title_surf = self.title_font.render(title_text, True, (255, 255, 0))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen.get_width()//2, 150)))

        # Exciting game description for kids
        game_text_lines = [
            "March like an elephant through the jungle!",
            "Each high knee stomp shakes the trees and makes fruit fall!",
            "Collect points for every fruit you get!"
        ]
        for i, line in enumerate(game_text_lines):
            surf = self.desc_font.render(line, True, (255, 255, 255))
            self.screen.blit(surf, surf.get_rect(center=(self.screen.get_width()//2, 250 + i*40)))

        # Parent PT goals (smaller font)
        pt_lines = [
            "PT Goal: Gross motor coordination, rhythm, bilateral movement.",
            "Exercise: March in place, lifting knees high, swinging arms."
        ]
        for i, line in enumerate(pt_lines):
            surf = self.desc_font.render(line, True, (240, 240, 240))
            self.screen.blit(surf, surf.get_rect(center=(self.screen.get_width()//2, 450 + i*30)))

        # Draw buttons
        self.start_button.draw()
        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Back button
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_selector"
            # Start button
            if self.start_button.is_clicked(mouse_pos):
                return "animal_march_camera"
        return None
