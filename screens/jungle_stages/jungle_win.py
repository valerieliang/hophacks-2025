# screens/jungle_win.py
import pygame
from ui.buttons import Button
from assets.fonts import dynapuff

class JungleWin:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Comic Sans MS", 80, bold=True)  # cute big letters
        self.small_font = dynapuff(40)
        self.back_button = Button(screen, text="Back to Jungle Selector", pos=(screen.get_width() // 2, screen.get_height() - 100))

    def draw(self):
        self.screen.fill((135, 206, 250))  # light blue background
        # Big "You Win!" text
        win_text = self.font.render("You Win!", True, (255, 215, 0))  # golden yellow
        win_rect = win_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(win_text, win_rect)

        # Back button
        self.back_button.draw()
        pygame.display.flip()

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                return "jungle_selector"
        return None
