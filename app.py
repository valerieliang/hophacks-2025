import pygame
import sys
from ui.screens import TitleScreen, StageSelectScreen
from ui.jungle_stage import JungleStage

pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w - 50, info.current_h - 100))
clock = pygame.time.Clock()

# Screens
title_screen = TitleScreen(screen)
stage_select = StageSelectScreen(screen)
jungle_stage = JungleStage(screen)

current_screen = "title"
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_screen == "title":
            result = title_screen.handle_event(event, mouse_pos)
            if result == "stage_select":
                current_screen = "stage_select"

        elif current_screen == "stage_select":
            result = stage_select.handle_event(event, mouse_pos)
            if result == "stage_1":  # jungle
                current_screen = "jungle_stage"

        elif current_screen == "jungle_stage":
            jungle_stage.handle_event(event, mouse_pos)

    # Draw
    if current_screen == "title":
        title_screen.draw()
    elif current_screen == "stage_select":
        stage_select.draw()
    elif current_screen == "jungle_stage":
        jungle_stage.draw()

    pygame.display.update()
    clock.tick(30)

pygame.quit()
sys.exit()