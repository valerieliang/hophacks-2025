import pygame
from ui.buttons import Button
from ui.back_button import BackButton
from assets.fonts import dynapuff

class StageSelect:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.back_button = BackButton(screen)
        
        # Load background
        self.background = pygame.image.load("assets/stages_background.jpg").convert()
        # Scale and center background to fill the screen, preserving aspect ratio
        bg_w, bg_h = self.background.get_size()
        scale = max(w / bg_w, h / bg_h)
        new_bg_w, new_bg_h = int(bg_w * scale), int(bg_h * scale)
        self.background = pygame.transform.smoothscale(self.background, (new_bg_w, new_bg_h))
        self.bg_offset = ((w - new_bg_w) // 2, (h - new_bg_h) // 2)
        
        # Jungle stage button
        self.jungle_button_img = pygame.image.load("assets/select_jungle.png").convert_alpha()
        button_width = int(w * 0.75)
        orig_w, orig_h = self.jungle_button_img.get_size()
        button_height = int(orig_h * (button_width / orig_w))
        self.jungle_button_img = pygame.transform.smoothscale(self.jungle_button_img, (button_width, button_height))
        self.button_size = (button_width, button_height)
        self.jungle_button_rect = self.jungle_button_img.get_rect(center=(w // 2, 200))
        
        # Placeholder stages (grey, unclickable)
        self.placeholder1_rect = pygame.Rect(0, 0, 0.75*button_width, 100)
        self.placeholder1_rect.center = (w // 2, 350)
        self.placeholder2_rect = pygame.Rect(0, 0, 0.75*button_width, 100)
        self.placeholder2_rect.center = (w // 2, 500)
        self.placeholder_color = (150, 150, 150)  # grey

        # Title font
        self.font = dynapuff(48, bold=True)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("Select a Stage", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 80)))

        # Jungle stage button
        self.screen.blit(self.jungle_button_img, self.jungle_button_rect)
        self.back_button.draw()

        # Grey placeholders
        pygame.draw.rect(self.screen, self.placeholder_color, self.placeholder1_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.placeholder_color, self.placeholder2_rect, border_radius=12)

        placeholder_font = dynapuff(24, italic=True)
        for rect in [self.placeholder1_rect, self.placeholder2_rect]:
            text_surf = placeholder_font.render("Coming Soon", True, (220, 220, 220))
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                return "title"  # go back to previous screen
            if self.jungle_button_rect.collidepoint(mouse_pos):
                return "jungle_intro"
        return None
