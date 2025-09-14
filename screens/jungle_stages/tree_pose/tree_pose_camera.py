import pygame
import cv2
import threading
import time
from ui.camera_manager import CameraManager
from ui.back_button import BackButton
from ui.camera_toggle import CameraToggleButton
from ui.buttons import Button
from assets.fonts import dynapuff
from minigames.tree_pose_logic import TreePoseLogic

class TreePoseCamera:
    def __init__(self, screen):
        self.screen = screen
        self.cap = None
        self.camera_manager = CameraManager(screen)
        self.back_button = BackButton(screen, pos=(60, 60))
        self.camera_button = CameraToggleButton(screen, size=200)
        self.font = dynapuff(40)
        self.camera_on = False

        # Threading
        self.frame = None
        self.keypoints = None
        self._stop_thread = False
        self._thread = None

        # Game logic
        self.game_logic = TreePoseLogic(hold_time=10)

        # Win overlay image
        self.win_image = pygame.image.load("assets/jungle_winner.png").convert_alpha()
        self.win_image = pygame.transform.smoothscale(self.win_image, self.screen.get_size())

        # Back-to-menu button (bottom center)
        screen_w, screen_h = screen.get_size()
        self.menu_button = Button(
            screen,
            text="Back to Menu",
            pos=(screen_w // 2, screen_h - 100),
            size=(300, 80)
        )

        # Debug flag
        self.show_debug = True

    # -------------------- Camera Thread --------------------
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
                        frame_surface, _, humans_keypoints = self.camera_manager.process_frame(frame)
                        self.frame = frame_surface

                        if humans_keypoints is None:
                            self.keypoints = []
                        else:
                            # Ensure each human has 17 keypoints
                            cleaned = []
                            for kp in humans_keypoints:
                                if len(kp) < 17:
                                    kp = kp + [[0.0, 0.0, 0.0]] * (17 - len(kp))
                                elif len(kp) > 17:
                                    kp = kp[:17]
                                cleaned.append(kp)
                            self.keypoints = cleaned
                    except Exception as e:
                        print(f"Error processing frame: {e}")
                        self.frame = None
                        self.keypoints = []
            time.sleep(0.01)

    def stop_camera_thread(self):
        self._stop_thread = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # -------------------- Draw --------------------
    def draw(self):
        # Always fill background
        self.screen.fill((102, 204, 255))

        # Draw camera frame if active
        if self.camera_on and self.frame is not None and not self.game_logic.game_over:
            self.screen.blit(self.frame, (0, 0))
            seconds_left = self.game_logic.update(self.keypoints)

            """# Draw visual indicators for pose detection
            if self.keypoints:
                self.draw_pose_indicators()"""

        elif not self.camera_on and not self.game_logic.game_over:
            pause_font = dynapuff(60)
            pause_text = pause_font.render("Press Camera to Begin", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2,
                                                     self.screen.get_height() // 2))
            self.screen.blit(pause_text, pause_rect)

        # Instructions
        if not self.game_logic.game_over and not self.game_logic.pose_achieved:
            instruction_font = dynapuff(30)
            instruction_text = instruction_font.render("Stand on one leg like a tree, then switch sides!", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(instruction_text, instruction_rect)

        # Draw countdown timer if pose detected
        if self.game_logic.pose_achieved and not self.game_logic.game_over:
            seconds_left = self.game_logic.get_time_remaining()
            if seconds_left is not None and seconds_left > 0:
                timer_text = self.font.render(f"Hold: {int(seconds_left)}s", True, (255, 0, 0))
                timer_rect = timer_text.get_rect(center=(self.screen.get_width() // 2, 100))
                self.screen.blit(timer_text, timer_rect)

                # Progress bar
                progress_width = 400
                progress_height = 20
                progress_x = (self.screen.get_width() - progress_width) // 2
                progress_y = 130
                
                # Background bar
                pygame.draw.rect(self.screen, (100, 100, 100), (progress_x, progress_y, progress_width, progress_height))
                
                # Progress bar
                progress = 1.0 - (seconds_left / self.game_logic.hold_time)
                filled_width = int(progress_width * progress)
                pygame.draw.rect(self.screen, (0, 255, 0), (progress_x, progress_y, filled_width, progress_height))

        # Debug information
        if self.show_debug and self.camera_on and not self.game_logic.game_over:
            self.draw_debug_info()

        # Buttons
        self.back_button.draw()
        if not self.game_logic.game_over:
            self.camera_button.draw()

        # Win overlay and menu button
        if self.game_logic.game_over:
            self.screen.blit(self.win_image, (0, 0))
            self.menu_button.draw()

        pygame.display.flip()

    def draw_pose_indicators(self):
        """Draw visual indicators for detected body parts"""
        if not self.keypoints:
            return
            
        # Use first detected human
        kp = self.keypoints[0]
        
        # Draw key points for tree pose
        keypoint_colors = {
            11: (255, 0, 0),    # left_hip - red
            12: (0, 255, 0),    # right_hip - green  
            13: (255, 255, 0),  # left_knee - yellow
            14: (255, 0, 255),  # right_knee - magenta
            15: (0, 255, 255),  # left_ankle - cyan
            16: (255, 128, 0),  # right_ankle - orange
        }
        
        for idx, color in keypoint_colors.items():
            if idx < len(kp) and kp[idx][2] > 0.5:  # confidence > 0.5
                x, y = int(kp[idx][0]), int(kp[idx][1])
                pygame.draw.circle(self.screen, color, (x, y), 8)

    def draw_debug_info(self):
        """Draw debug information"""
        debug_font = pygame.font.Font(None, 24)
        y_offset = 10
        
        # Human count
        human_count = len(self.keypoints) if self.keypoints else 0
        debug_text = debug_font.render(f"Humans detected: {human_count}", True, (255, 255, 0))
        self.screen.blit(debug_text, (10, y_offset))
        y_offset += 25
        
        # Game state
        if self.keypoints:
            status = "Pose Achieved" if self.game_logic.pose_achieved else "Getting Ready"
            status_text = debug_font.render(f"Status: {status}", True, (255, 255, 0))
            self.screen.blit(status_text, (10, y_offset))
            y_offset += 25
            
            # Show which leg is detected as lifted (if any)
            debug_info = self.game_logic.get_debug_info()
            if debug_info:
                debug_text = debug_font.render(debug_info, True, (255, 255, 0))
                self.screen.blit(debug_text, (10, y_offset))

    # -------------------- Event Handling --------------------
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "tree_pose_intro"

            # Camera toggle (start/stop)
            if not self.game_logic.game_over and self.camera_button.is_clicked(mouse_pos):
                self.camera_on = not self.camera_on
                if self.camera_on:
                    self.start_camera_thread()
                else:
                    self.stop_camera_thread()

            # Back to menu button after game over
            if self.game_logic.game_over and self.menu_button.is_clicked(mouse_pos):
                self.stop_camera_thread()
                return "jungle_selector"

        # Toggle debug with 'D' key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            self.show_debug = not self.show_debug

        return None