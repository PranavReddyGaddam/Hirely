"""
Gesture and Fidgeting Detection Module
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque

from app.cv.utils.landmark_utils import (
    calculate_distance,
    calculate_hand_velocity,
    is_hand_near_face,
    calculate_position_variance
)


class GestureDetector:
    """Detects hand gestures and fidgeting behaviors"""
    
    def __init__(self, config):
        self.config = config
        
        # Thresholds
        self.face_touch_threshold = config.FACE_TOUCH_DISTANCE_THRESHOLD
        self.hand_velocity_threshold = config.HAND_VELOCITY_THRESHOLD
        self.hand_fidget_frequency = config.HAND_FIDGET_FREQUENCY
        self.gesture_amplitude_threshold = config.HAND_GESTURE_AMPLITUDE_THRESHOLD
        
        # History tracking
        self.left_hand_positions = deque(maxlen=90)   # 3 seconds at 30fps
        self.right_hand_positions = deque(maxlen=90)
        self.face_touch_counter = 0
        self.fidget_counter = 0
        
        # State tracking
        self.is_touching_face = False
        self.touch_duration = 0
        
    def detect(self, hand_landmarks_list: List, face_landmarks,
               image_width: int, image_height: int) -> Dict:
        """Detect gestures and fidgeting from hand landmarks"""
        
        result = {
            'hands_detected': len(hand_landmarks_list) if hand_landmarks_list else 0,
            'left_hand_detected': False,
            'right_hand_detected': False,
            'face_touching': False,
            'hand_fidgeting': False,
            'excessive_gesturing': False,
            'hand_near_head': False,
            'crossed_arms': False,
            'face_touch_count': self.face_touch_counter,
            'fidget_count': self.fidget_counter
        }
        
        if not hand_landmarks_list:
            return result
        
        # Process each detected hand
        for hand_idx, hand_landmarks in enumerate(hand_landmarks_list):
            if hand_idx >= 2:  # Max 2 hands
                break
            
            # Extract hand position (wrist)
            wrist = hand_landmarks.landmark[0]
            hand_position = (wrist.x, wrist.y)
            
            # Determine which hand (simplified - would need handedness from MediaPipe)
            if hand_idx == 0:
                self.left_hand_positions.append(hand_position)
                result['left_hand_detected'] = True
            else:
                self.right_hand_positions.append(hand_position)
                result['right_hand_detected'] = True
            
            # Check face touching
            if face_landmarks:
                if self._check_face_touching(hand_landmarks, face_landmarks):
                    result['face_touching'] = True
                    self.is_touching_face = True
                    self.touch_duration += 1
                    if self.touch_duration == 1:  # First frame of touch
                        self.face_touch_counter += 1
                else:
                    if self.is_touching_face:
                        self.is_touching_face = False
                        self.touch_duration = 0
            
            # Check if hand near head (playing with hair)
            if self._check_hand_near_head(hand_landmarks, face_landmarks):
                result['hand_near_head'] = True
        
        # Detect fidgeting (requires history)
        result['hand_fidgeting'] = self._detect_fidgeting()
        
        # Detect excessive gesturing
        result['excessive_gesturing'] = self._detect_excessive_gesturing()
        
        # Detect crossed arms (requires both hands)
        if len(hand_landmarks_list) >= 2:
            result['crossed_arms'] = self._detect_crossed_arms(hand_landmarks_list)
        
        return result
    
    def _check_face_touching(self, hand_landmarks, face_landmarks) -> bool:
        """Check if hand is touching face"""
        # Get key hand points (fingertips)
        fingertip_indices = [4, 8, 12, 16, 20]  # thumb to pinky tips
        
        # Get key face points (more focused on face area)
        face_region_indices = [
            234, 93, 132, 58, 172,  # Left face
            454, 323, 361, 288, 397,  # Right face
            10, 151, 9, 8,  # Forehead/nose
        ]
        
        for finger_idx in fingertip_indices:
            finger = hand_landmarks.landmark[finger_idx]
            finger_pos = (finger.x, finger.y)
            
            for face_idx in face_region_indices:
                face_point = face_landmarks.landmark[face_idx]
                face_pos = (face_point.x, face_point.y)
                
                distance = calculate_distance(finger_pos, face_pos)
                
                if distance < self.face_touch_threshold:
                    return True
        
        return False
    
    def _check_hand_near_head(self, hand_landmarks, face_landmarks) -> bool:
        """Check if hand is near head region (playing with hair)"""
        if not face_landmarks:
            return False
        
        # Get hand center
        wrist = hand_landmarks.landmark[0]
        hand_pos = (wrist.x, wrist.y)
        
        # Get head top region (forehead, top of head)
        head_top_indices = [10, 338, 297, 332, 284]  # Top of face
        
        for idx in head_top_indices:
            head_point = face_landmarks.landmark[idx]
            head_pos = (head_point.x, head_point.y)
            
            distance = calculate_distance(hand_pos, head_pos)
            
            # Larger threshold for "near head" vs touching face
            if distance < self.face_touch_threshold * 2:
                return True
        
        return False
    
    def _detect_fidgeting(self) -> bool:
        """Detect hand fidgeting based on movement patterns"""
        # Need sufficient history
        if len(self.left_hand_positions) < 30 and len(self.right_hand_positions) < 30:
            return False
        
        # Calculate velocity for each hand
        left_fidgeting = False
        right_fidgeting = False
        
        if len(self.left_hand_positions) >= 30:
            left_velocity = calculate_hand_velocity(list(self.left_hand_positions)[-30:])
            left_variance = calculate_position_variance(list(self.left_hand_positions), 30)
            
            # Fidgeting: high velocity but small movements (high variance, constrained area)
            if left_velocity > self.hand_velocity_threshold and left_variance > 0.001:
                left_fidgeting = True
        
        if len(self.right_hand_positions) >= 30:
            right_velocity = calculate_hand_velocity(list(self.right_hand_positions)[-30:])
            right_variance = calculate_position_variance(list(self.right_hand_positions), 30)
            
            if right_velocity > self.hand_velocity_threshold and right_variance > 0.001:
                right_fidgeting = True
        
        is_fidgeting = left_fidgeting or right_fidgeting
        
        if is_fidgeting:
            self.fidget_counter += 1
        
        return is_fidgeting
    
    def _detect_excessive_gesturing(self) -> bool:
        """Detect wild or excessive hand gestures"""
        # Check amplitude of hand movements
        if len(self.left_hand_positions) < 10 and len(self.right_hand_positions) < 10:
            return False
        
        # Calculate range of motion in recent frames
        def get_movement_range(positions):
            if len(positions) < 10:
                return 0
            recent = list(positions)[-30:]
            x_coords = [p[0] for p in recent]
            y_coords = [p[1] for p in recent]
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            return max(x_range, y_range)
        
        left_range = get_movement_range(self.left_hand_positions)
        right_range = get_movement_range(self.right_hand_positions)
        
        # Excessive if movement range is very large
        return (left_range > self.gesture_amplitude_threshold or 
                right_range > self.gesture_amplitude_threshold)
    
    def _detect_crossed_arms(self, hand_landmarks_list: List) -> bool:
        """Detect if arms are crossed"""
        if len(hand_landmarks_list) < 2:
            return False
        
        # Get wrist positions
        left_hand = hand_landmarks_list[0]
        right_hand = hand_landmarks_list[1]
        
        left_wrist = left_hand.landmark[0]
        right_wrist = right_hand.landmark[0]
        
        # Crossed arms: hands are on opposite sides and close together
        # Simplified heuristic
        hands_close = calculate_distance(
            (left_wrist.x, left_wrist.y),
            (right_wrist.x, right_wrist.y)
        ) < 0.2
        
        # Check if hands are near torso center
        hands_centered = (0.3 < left_wrist.x < 0.7 and 0.3 < right_wrist.x < 0.7)
        
        return hands_close and hands_centered
    
    def reset_counters(self):
        """Reset gesture counters"""
        self.face_touch_counter = 0
        self.fidget_counter = 0
