import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from ui.desc_font import DescFont
from assets.fonts import dynapuff
import os

class TreePoseIntro:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()

        # Load title image
        self.title_image = pygame.image.load(os.path.join("assets", "tree_pose.png")).convert_alpha()
        self.title_rect = self.title_image.get_rect(midtop=(w // 2, -25))

        # Description fonts
        self.game_lines = DescFont(screen, size=22, bold=False, color=(255, 255, 255), margin=50)
        self.parent_lines = DescFont(screen, size=18, bold=False, color=(240, 240, 240), margin=50)

        # Start button to toggle camera
        width = int(w * 0.5)
        self.start_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 80),
            size=(width, 60),
            text="Start Exercise"
        )

        # Back button
        self.back_button = BackButton(screen, pos=(60, 60))

    def draw(self):
        self.screen.fill((102, 204, 255))  # bright, fun blue background

        # Draw title image
        self.screen.blit(self.title_image, self.title_rect)

        # Exciting game description for kids
        game_text = ("Stand tall like a tree and hold your balance! The longer you balance, the taller your tree grows.")

        # Start y-coordinate below the title
        y_start = self.title_rect.bottom - 25
        self.game_lines.render_text(game_text, y_start)

        # Parent PT goals (smaller font)
        pt_text_1 = "PT Goal: Static balance, core stability."
        pt_text_2 = "Exercise: Stand on one leg, switch sides after 10 sec."

        y_start += 80  # space between kid description and parent info
        self.parent_lines.render_text(pt_text_1, y_start)
        self.parent_lines.render_text(pt_text_2, y_start + 30)

        # Draw buttons
        self.start_button.draw()
        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_selector"
            if self.start_button.is_clicked(mouse_pos):
                return "tree_pose_camera"
        return None