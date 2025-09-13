import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from ui.desc_font import DescFont
from assets.fonts import dynapuff

class TreePoseIntro:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()

        # Title font for kids
        self.title_font = dynapuff(64, bold=True) 

        # Description fonts
        self.game_lines = DescFont(screen, size=24, bold=False, color=(255, 255, 255), margin=50)
        self.parent_lines = DescFont(screen, size=20, bold=False, color=(240, 240, 240), margin=50)

        # Start button to toggle camera
        width = int(w * 0.5)
        self.start_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 100),
            size=(width, 80),
            text="Start Exercise"
        )

        # Back button
        self.back_button = BackButton(screen, pos=(60, 60))

    def draw(self):
        self.screen.fill((102, 204, 255))  # bright, fun blue background

        # Kid-friendly title / intro
        title_text = "Tree Pose"
        title_surf = self.title_font.render(title_text, True, (255, 255, 0))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen.get_width()//2, 150)))

        # Exciting game description for kids
        game_text = ("You’re a tree in the jungle. The longer you balance on one foot," 
                     "the taller your tree grows. Birds land on your branches.")

        # Start y-coordinate below the title
        y_start = 250
        self.game_lines.render_text(game_text, y_start)

        # Parent PT goals (smaller font)
        pt_text = ("PT Goal: Static balance, core stability."
                   "Exercise: Stand on one leg, switch sides after \~20 seconds")

        y_start += 120  # space between kid description and parent info
        self.parent_lines.render_text(pt_text, y_start)

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
                return "tree_pose_camera"
        return None
