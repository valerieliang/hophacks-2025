import pygame
from assets.fonts import dynapuff

class DescFont:
    def __init__(self, screen, size=24, bold=False, font_name=None, color=(255,255,255), margin=50):
        self.screen = screen
        self.size = size
        self.bold = bold
        self.color = color
        self.margin = margin
        self.font = dynapuff(size)

    def render_text(self, text, top_y):
        words = text.split(' ')
        lines = []
        current_line = ""
        max_width = self.screen.get_width() - 2 * self.margin

        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y = top_y
        for line in lines:
            surf = self.font.render(line, True, self.color)
            x = self.margin + (max_width - surf.get_width()) // 2  # center within margin
            self.screen.blit(surf, (x, y))
            y += self.font.get_linesize()

        return y 
