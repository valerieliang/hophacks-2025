import time
from collections import deque

class TreePoseLogic:
    def __init__(self, hold_time=10, knee_lift_threshold=50, stability_threshold=20, confidence_threshold=0.5):
        """
        hold_time: seconds the pose must be held to win
        knee_lift_threshold: minimum y difference between knees to consider a leg lifted  
        stability_threshold: max allowed movement for supporting leg
        confidence_threshold: minimum confidence for keypoint detection
        """
        self.hold_time = hold_time
        self.knee_lift_threshold = knee_lift_threshold
        self.stability_threshold = stability_threshold
        self.confidence_threshold = confidence_threshold
        
        # Game state
        self.in_pose_start = None
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False
        
        # Pose detection
        self.last_support_knee_y = None
        self.lifted_leg = None
        
        # Smoothing for stability detection
        self.support_history = deque(maxlen=8)  # Keep last 8 positions
        self.pose_consistency_frames = 0
        self.required_consistency = 15  # Frames of consistent pose before starting timer
        
        # Debug info
        self.debug_info = ""

    def reset(self):
        """Reset the game state"""
        self.in_pose_start = None
        self.timer_start = None
        self.pose_achieved = False
        self.game_over = False
        self.last_support_knee_y = None
        self.lifted_leg = None
        self.support_history.clear()
        self.pose_consistency_frames = 0
        self.debug_info = ""

    def extract_keypoints(self, keypoints_list):
        """Extract relevant keypoints from the list format"""
        if not keypoints_list or len(keypoints_list) == 0:
            return None
            
        # Use first detected human
        kp = keypoints_list[0]
        
        # Extract hip, knee, and ankle positions
        keypoint_data = {}
        keypoint_indices = {
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16
        }
        
        for name, idx in keypoint_indices.items():
            if idx < len(kp) and kp[idx][2] >= self.confidence_threshold:
                keypoint_data[name] = (kp[idx][0], kp[idx][1])
            else:
                # Missing or low confidence keypoint
                return None
                
        return keypoint_data

    def detect_tree_pose(self, keypoints):
        """
        Detect if person is in tree pose (standing on one leg)
        Returns: (is_in_pose, lifted_leg, support_knee_y)
        """
        required_points = ['left_hip', 'right_hip', 'left_knee', 'right_knee']
        if not all(point in keypoints for point in required_points):
            return False, None, None

        left_hip_y = keypoints['left_hip'][1]
        right_hip_y = keypoints['right_hip'][1]
        left_knee_y = keypoints['left_knee'][1]
        right_knee_y = keypoints['right_knee'][1]
        
        # Calculate average hip level as reference
        avg_hip_y = (left_hip_y + right_hip_y) / 2
        
        # Check if left knee is significantly higher than right knee
        left_knee_lift = avg_hip_y - left_knee_y
        right_knee_lift = avg_hip_y - right_knee_y
        
        knee_difference = abs(left_knee_y - right_knee_y)
        
        # Determine which leg is lifted based on knee height difference
        if knee_difference >= self.knee_lift_threshold:
            if left_knee_y < right_knee_y:
                # Left knee is higher (left leg lifted)
                return True, 'left', right_knee_y
            else:
                # Right knee is higher (right leg lifted)  
                return True, 'right', left_knee_y
        
        return False, None, None

    def check_stability(self, current_support_y):
        """Check if the supporting leg is stable"""
        self.support_history.append(current_support_y)
        
        if len(self.support_history) < 5:
            return False
            
        # Calculate variance in support leg position
        positions = list(self.support_history)
        avg_pos = sum(positions) / len(positions)
        variance = sum((pos - avg_pos) ** 2 for pos in positions) / len(positions)
        stability = variance ** 0.5  # Standard deviation
        
        return stability <= self.stability_threshold

    def update(self, keypoints_list):
        """
        Update game state with new keypoints
        Returns: seconds left if countdown active, None otherwise
        """
        # Extract keypoints from list format
        keypoints = self.extract_keypoints(keypoints_list)
        
        if not keypoints:
            # Reset pose detection if no valid keypoints
            self.pose_consistency_frames = 0
            self.in_pose_start = None
            self.timer_start = None
            self.pose_achieved = False
            self.support_history.clear()
            self.debug_info = "No valid keypoints detected"
            return None

        # Detect tree pose
        is_in_pose, lifted_leg, support_knee_y = self.detect_tree_pose(keypoints)
        
        if is_in_pose:
            # Check stability of supporting leg
            is_stable = self.check_stability(support_knee_y)
            
            if is_stable and lifted_leg == self.lifted_leg:
                # Consistent pose detected
                self.pose_consistency_frames += 1
                self.debug_info = f"Consistent pose: {lifted_leg} leg lifted, frames: {self.pose_consistency_frames}"
                
                if self.pose_consistency_frames >= self.required_consistency:
                    if not self.timer_start:
                        # Start the countdown timer
                        self.timer_start = time.time()
                        self.pose_achieved = True
                        self.debug_info = f"Timer started! {lifted_leg} leg lifted"
            else:
                # Pose changed or became unstable
                if lifted_leg != self.lifted_leg:
                    self.pose_consistency_frames = 1  # Reset but don't zero (new pose detected)
                    self.lifted_leg = lifted_leg
                    self.support_history.clear()
                else:
                    self.pose_consistency_frames = max(0, self.pose_consistency_frames - 2)  # Decay
                
                self.debug_info = f"Pose unstable or changed: {lifted_leg} leg, stability: {is_stable}"
            
            self.lifted_leg = lifted_leg
            
        else:
            # Not in tree pose
            self.pose_consistency_frames = max(0, self.pose_consistency_frames - 3)  # Quick decay
            self.timer_start = None
            self.pose_achieved = False
            self.support_history.clear()
            self.debug_info = "Not in tree pose"

        # Handle countdown
        if self.timer_start and self.pose_achieved:
            elapsed = time.time() - self.timer_start
            
            if not is_in_pose or not self.check_stability(support_knee_y):
                # Pose broken, reset timer but keep some progress
                self.timer_start = None
                self.pose_achieved = False
                self.debug_info += " - Pose broken, timer reset"
                return None
                
            if elapsed >= self.hold_time:
                self.game_over = True
                self.debug_info = "Game completed!"
                return 0
            else:
                remaining = self.hold_time - elapsed
                self.debug_info = f"Holding pose: {remaining:.1f}s remaining"
                return remaining

        return None

    def get_time_remaining(self):
        """Get remaining time for the current hold"""
        if self.timer_start and self.pose_achieved:
            elapsed = time.time() - self.timer_start
            return max(0, self.hold_time - elapsed)
        return None

    def get_debug_info(self):
        """Get debug information string"""
        return self.debug_info