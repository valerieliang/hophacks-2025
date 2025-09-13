import pygame, sys
from screens.title_screen import TitleScreen
from screens.stage_select import StageSelect
from screens.jungle_stages.jungle_intro import JungleIntro
from screens.jungle_stages.jungle_selector import JungleSelector
from screens.jungle_stages.animal_march.animal_march_intro import AnimalMarchIntro
from screens.jungle_stages.animal_march.animal_march_camera import AnimalMarchCamera
from screens.jungle_stages.tree_pose.tree_pose_intro import TreePoseIntro
from screens.jungle_stages.tree_pose.tree_pose_camera import TreePoseCamera
from screens.jungle_stages.river_crossing.river_crossing_intro import RiverCrossingIntro
from screens.jungle_stages.river_crossing.river_crossing_camera import RiverCrossingCamera

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
    "animal_march_intro": AnimalMarchIntro(screen),
    "animal_march_camera":AnimalMarchCamera(screen),
    "tree_pose_intro": TreePoseIntro(screen),  
    "tree_pose_camera": TreePoseCamera(screen),
    "river_crossing_intro": RiverCrossingIntro(screen),
    "river_crossing_camera": RiverCrossingCamera(screen)
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
