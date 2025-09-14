import pygame
import cv2
import threading
import time
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button
from assets.fonts import dynapuff
from minigames.river_crossing_logic import RiverCrossingGame

class RiverCrossingCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.camera_button = CameraToggleButton(screen, size=180)
        self.font = dynapuff(40)
        self.camera_on = False

        # Threading
        self.surface = None
        self.offset = (0,0)
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = RiverCrossingGame()
        # Set screen dimensions for proper stone placement
        self.game_logic.set_screen_dimensions(screen.get_width(), screen.get_height())

        # Win overlay
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button
        sw, sh = screen.get_size()
        self.menu_button = Button(screen, text="Back to Menu", pos=(sw//2, sh-100), size=(300, 80))

        # Debug flag
        self.show_debug = True

    # --- Camera Thread ---
    def start_camera_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera!")
            return
        self._stop_thread = False
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while not self._stop_thread:
            if self.camera_on and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    try:
                        # Mirror the frame horizontally for natural interaction
                        frame = cv2.flip(frame, 1)
                        
                        # Use process_frame method which returns frame_surface, _, humans_keypoints
                        frame_surface, _, humans_keypoints = self.camera_manager.process_frame(frame)
                        
                        if frame_surface is not None:
                            self.surface = frame_surface
                            self.offset = (0, 0)  # Assuming full screen frame
                            
                            # Always store as list of humans (list of lists)
                            if humans_keypoints is None:
                                self.keypoints = []
                            else:
                                cleaned = []
                                for kp in humans_keypoints:
                                    # Make sure each human has exactly 17 keypoints
                                    if len(kp) < 17:
                                        kp = kp + [[0.0, 0.0, 0.0]] * (17 - len(kp))
                                    elif len(kp) > 17:
                                        kp = kp[:17]
                                    cleaned.append(kp)
                                self.keypoints = cleaned
                    except Exception as e:
                        print(f"Error processing frame: {e}")
                        self.surface = None
                        self.keypoints = []
            time.sleep(0.01)

    def stop_camera_thread(self):
        self._stop_thread = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # --- Draw ---
    def draw(self):
        self.screen.fill((102,204,255))

        if self.camera_on and self.surface:
            # --- Update game logic each frame ---
            if self.keypoints:
                self.game_logic.update(self.keypoints)

            # --- Draw camera ---
            self.screen.blit(self.surface, self.offset)

            # --- Draw keypoints (feet) ---
            for i, kp in enumerate(self.keypoints or []):
                feet = self.game_logic.feet_positions(kp)
                if feet:
                    ox, oy = self.offset
                    for fx, fy in feet:
                        # Draw feet as yellow circles
                        pygame.draw.circle(self.screen, (255,255,0), (fx+ox, fy+oy), 15)
                        
                        # Draw foot coordinates for debugging
                        if self.show_debug:
                            debug_font = pygame.font.Font(None, 20)
                            coord_text = debug_font.render(f"({fx},{fy})", True, (255,255,255))
                            self.screen.blit(coord_text, (fx+ox+20, fy+oy-10))

            # --- Draw current stone ---
            self.game_logic.draw_stone_on_surface(self.screen, self.offset)

            # --- Draw debug foot positions (optional) ---
            if self.show_debug:
                self.game_logic.draw_foot_positions(self.screen, self.offset)

            # --- Draw debug info ---
            if self.show_debug:
                self.draw_debug_info()

        elif not self.camera_on and not self.game_logic.game_over:
            text_font = dynapuff(60)
            text = text_font.render("Press Camera to Begin", True, (255,255,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, rect)

        # --- Score ---
        score_text = self.font.render(f"Score: {self.game_logic.score}", True, (255,255,255))
        score_rect = score_text.get_rect(bottomright=(self.screen.get_width()-20, self.screen.get_height()-20))
        self.screen.blit(score_text, score_rect)

        # --- Progress indicator ---
        progress_text = self.font.render(f"Progress: {self.game_logic.score}/{self.game_logic.points_to_win}", True, (255,255,255))
        progress_rect = progress_text.get_rect(bottomleft=(20, self.screen.get_height()-60))
        self.screen.blit(progress_text, progress_rect)

        # --- Buttons ---
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # --- Win overlay ---
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0,0))
            self.menu_button.draw()

        pygame.display.flip()

    def draw_debug_info(self):
        """Draw debug information"""
        debug_font = pygame.font.Font(None, 24)
        y_offset = 10
        
        # Human count
        human_count = len(self.keypoints) if self.keypoints else 0
        debug_text = debug_font.render(f"Humans detected: {human_count}", True, (255, 255, 0))
        self.screen.blit(debug_text, (10, y_offset))
        y_offset += 25
        
        # Show foot coordinates
        if self.keypoints:
            for i, kp in enumerate(self.keypoints):
                feet = self.game_logic.feet_positions(kp)
                if feet:
                    for j, (fx, fy) in enumerate(feet):
                        coord_text = debug_font.render(f"Foot {j+1}: ({fx},{fy})", True, (255, 255, 0))
                        self.screen.blit(coord_text, (10, y_offset))
                        y_offset += 20
        
        # Current stone info
        if self.game_logic.current_stone:
            stone_x, stone_y = self.game_logic.current_stone
            stone_text = debug_font.render(f"Current stone: ({stone_x}, {stone_y})", True, (255, 255, 0))
            self.screen.blit(stone_text, (10, y_offset))
            y_offset += 25
        else:
            no_stone_text = debug_font.render("No stone generated yet", True, (255, 255, 0))
            self.screen.blit(no_stone_text, (10, y_offset))
            y_offset += 25
        
        # Game status
        status_text = debug_font.render(f"Game over: {self.game_logic.game_over}", True, (255, 255, 0))
        self.screen.blit(status_text, (10, y_offset))
        y_offset += 25
        
        # Hit cooldown
        cooldown_text = debug_font.render(f"Hit cooldown: {self.game_logic.hit_cooldown}", True, (255, 255, 0))
        self.screen.blit(cooldown_text, (10, y_offset))
        y_offset += 25
        
        # Current foot positions count
        foot_count = len(self.game_logic.current_foot_positions)
        foot_count_text = debug_font.render(f"Tracked feet: {foot_count}", True, (255, 255, 0))
        self.screen.blit(foot_count_text, (10, y_offset))

    # --- Event Handling ---
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "river_crossing_intro"
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
                if self.camera_on:
                    self.start_camera_thread()
                else:
                    self.stop_camera_thread()
            if self.game_logic.game_over and self.menu_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "jungle_selector"
        
        # Toggle debug with 'D' key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            self.show_debug = not self.show_debug
            
        # Reset game with 'R' key (for testing)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.game_logic.reset_game()
            
        return None