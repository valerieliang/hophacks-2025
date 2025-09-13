import pygame, sys
from screens.title_screen import TitleScreen
from screens.stage_select import StageSelect
from screens.jungle_stages.jungle_intro import JungleIntro
from screens.jungle_stages.jungle_selector import JungleSelector
from screens.jungle_stages.jungle_stage import JungleStage

pygame.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w - 50, info.current_h - 100
screen = pygame.display.set_mode((screen_height, screen_height))

clock = pygame.time.Clock()

# Screen manager
screens = {
    "title": TitleScreen(screen),
    "stage_select": StageSelect(screen),
    "jungle_intro": JungleIntro(screen),
    "jungle_selector": JungleSelector(screen),
    "jungle_stage": JungleStage(screen)
}
current_screen = "title"

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            result = screens[current_screen].handle_event(event, mouse_pos)
            if result and result in screens:
                current_screen = result

    screens[current_screen].draw()
    pygame.display.update()
    clock.tick(30)

pygame.quit()
sys.exit()
