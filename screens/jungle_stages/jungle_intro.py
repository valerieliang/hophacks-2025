import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from ui.desc_font import DescFont
from assets.fonts import dynapuff

ICON_DIM = 500

class JungleIntro:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.title_font = dynapuff(72, bold=True)
        self.desc_font = DescFont(screen, size=24, bold=False, color=(240, 240, 240), margin=50)
        self.back_button = BackButton(screen)

        # Load stage icon
        self.icon = pygame.image.load("assets/jungle_adventure_icon.png").convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (ICON_DIM, ICON_DIM))  # adjust size as needed

        button_width = int(w * 0.5)
        button_height = 80 
        self.start_button = Button(
            screen,
            image=None,
            pos=(w // 2, h - 100),
            size=(button_width, button_height),
            text="Select Mini-Game"
        )

    def draw(self):
        self.screen.fill((34, 139, 34))

        # Draw the stage icon in the middle top
        icon_rect = self.icon.get_rect(centerx=self.screen.get_width() // 2)
        icon_rect.top = 0
        self.screen.blit(self.icon, icon_rect)

        # Description under the image (for parents)
        description = ("In this stage, children practice coordination, balance, and gross motor skills "
                       "through fun jungle-themed games. Each exercise is wrapped in a story to keep them engaged.")

        # Start y-coordinate just below the icon
        y_start = icon_rect.bottom -10
        self.desc_font.render_text(description, y_start)

        # Draw buttons
        self.start_button.draw()
        self.back_button.draw()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.is_clicked(mouse_pos):
                return "jungle_selector"
            if self.back_button.is_clicked(mouse_pos):
                return "stage_select"  # go back to stage select
        
        return None
