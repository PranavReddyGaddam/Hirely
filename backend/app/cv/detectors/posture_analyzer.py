"""
Body Posture Analysis Module
"""

import numpy as np
from typing import Dict, Tuple, List, Optional
from collections import deque

from app.cv.utils.landmark_utils import (
    calculate_angle_vertical,
    calculate_distance,
    calculate_position_variance,
    smooth_value
)


class PostureAnalyzer:
    """Analyzes body posture from MediaPipe pose landmarks"""
    
    def __init__(self, config):
        self.config = config
        
        # Thresholds
        self.neck_angle_good_min = config.NECK_ANGLE_GOOD_MIN
        self.neck_angle_good_max = config.NECK_ANGLE_GOOD_MAX
        self.neck_angle_bad = config.NECK_ANGLE_BAD
        
        self.torso_angle_good_min = config.TORSO_ANGLE_GOOD_MIN
        self.torso_angle_good_max = config.TORSO_ANGLE_GOOD_MAX
        self.torso_angle_slouch = config.TORSO_ANGLE_SLOUCH
        self.torso_angle_lean_back = config.TORSO_ANGLE_LEAN_BACK
        
        self.lean_forward_engaged = config.LEAN_FORWARD_ENGAGED
        self.lean_forward_max = config.LEAN_FORWARD_MAX
        
        # History for temporal analysis
        self.shoulder_positions = deque(maxlen=90)  # 3 seconds
        self.neck_angles = deque(maxlen=30)
        self.torso_angles = deque(maxlen=30)
        
        # Baseline (set during calibration)
        self.baseline_neck_angle = 20.0
        self.baseline_torso_angle = 10.0
        self.baseline_shoulder_y = 0.5
        
        # Smoothing
        self.smoothed_neck_angle = 0.0
        self.smoothed_torso_angle = 0.0
        
    def calibrate(self, pose_landmarks_list: List) -> bool:
        """Calibrate baseline posture from multiple frames"""
        if not pose_landmarks_list or len(pose_landmarks_list) < 10:
            return False
        
        neck_angles = []
        torso_angles = []
        shoulder_y_positions = []
        
        for landmarks in pose_landmarks_list:
            if landmarks:
                neck_angle = self._calculate_neck_angle(landmarks)
                torso_angle = self._calculate_torso_angle(landmarks)
                
                if neck_angle > 0:
                    neck_angles.append(neck_angle)
                if torso_angle > 0:
                    torso_angles.append(torso_angle)
                
                # Record shoulder position
                left_shoulder = landmarks.landmark[11]
                right_shoulder = landmarks.landmark[12]
                avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                shoulder_y_positions.append(avg_shoulder_y)
        
        if neck_angles:
            self.baseline_neck_angle = np.mean(neck_angles)
        if torso_angles:
            self.baseline_torso_angle = np.mean(torso_angles)
        if shoulder_y_positions:
            self.baseline_shoulder_y = np.mean(shoulder_y_positions)
        
        print(f"[PostureAnalyzer] Calibration complete - Neck: {self.baseline_neck_angle:.1f}°, Torso: {self.baseline_torso_angle:.1f}°")
        return True
    
    def analyze(self, pose_landmarks) -> Dict:
        """Analyze posture from pose landmarks"""
        
        if not pose_landmarks:
            return self._default_result()
        
        # Calculate angles
        neck_angle = self._calculate_neck_angle(pose_landmarks)
        torso_angle = self._calculate_torso_angle(pose_landmarks)
        
        # Smooth values
        self.smoothed_neck_angle = smooth_value(neck_angle, self.smoothed_neck_angle, 0.7)
        self.smoothed_torso_angle = smooth_value(torso_angle, self.smoothed_torso_angle, 0.7)
        
        # Update history
        self.neck_angles.append(self.smoothed_neck_angle)
        self.torso_angles.append(self.smoothed_torso_angle)
        
        # Track shoulder position for fidgeting
        left_shoulder = pose_landmarks.landmark[11]
        right_shoulder = pose_landmarks.landmark[12]
        shoulder_center = ((left_shoulder.x + right_shoulder.x) / 2,
                          (left_shoulder.y + right_shoulder.y) / 2)
        self.shoulder_positions.append(shoulder_center)
        
        # Calculate additional features
        is_slouching = self._detect_slouching(self.smoothed_torso_angle, self.smoothed_neck_angle)
        is_leaning_back = self._detect_leaning_back(self.smoothed_torso_angle)
        is_leaning_forward = self._detect_forward_lean(self.smoothed_torso_angle)
        shoulder_alignment = self._check_shoulder_alignment(pose_landmarks)
        is_fidgeting = self._detect_fidgeting()
        
        # Classify posture
        posture_status, confidence = self._classify_posture(
            self.smoothed_neck_angle, self.smoothed_torso_angle,
            is_slouching, is_leaning_back, is_leaning_forward,
            shoulder_alignment
        )
        
        return {
            'posture_status': posture_status,
            'confidence': confidence,
            'neck_angle': self.smoothed_neck_angle,
            'torso_angle': self.smoothed_torso_angle,
            'is_slouching': is_slouching,
            'is_leaning_back': is_leaning_back,
            'is_leaning_forward': is_leaning_forward,
            'shoulder_alignment': shoulder_alignment,
            'is_fidgeting': is_fidgeting
        }
    
    def _calculate_neck_angle(self, pose_landmarks) -> float:
        """Calculate neck inclination angle"""
        # Landmarks: ear (7 or 8), shoulder (11 or 12)
        left_ear = pose_landmarks.landmark[7]
        left_shoulder = pose_landmarks.landmark[11]
        
        # Use left side (or average both)
        ear_point = (left_ear.x, left_ear.y)
        shoulder_point = (left_shoulder.x, left_shoulder.y)
        
        angle = calculate_angle_vertical(shoulder_point, ear_point)
        return angle
    
    def _calculate_torso_angle(self, pose_landmarks) -> float:
        """Calculate torso inclination angle"""
        # Landmarks: shoulder (11 or 12), hip (23 or 24)
        left_shoulder = pose_landmarks.landmark[11]
        left_hip = pose_landmarks.landmark[23]
        
        shoulder_point = (left_shoulder.x, left_shoulder.y)
        hip_point = (left_hip.x, left_hip.y)
        
        angle = calculate_angle_vertical(hip_point, shoulder_point)
        return angle
    
    def _detect_slouching(self, torso_angle: float, neck_angle: float) -> bool:
        """Detect if person is slouching"""
        # Slouching: excessive torso or neck angle
        return (torso_angle > self.torso_angle_slouch or 
                neck_angle > self.neck_angle_bad)
    
    def _detect_leaning_back(self, torso_angle: float) -> bool:
        """Detect if person is leaning back excessively"""
        # Negative torso angle (if we track direction) or very high angle
        return torso_angle > self.torso_angle_lean_back
    
    def _detect_forward_lean(self, torso_angle: float) -> bool:
        """Detect if person is leaning forward (engaged)"""
        # Moderate forward lean is good
        return (self.lean_forward_engaged < torso_angle < self.lean_forward_max)
    
    def _check_shoulder_alignment(self, pose_landmarks) -> str:
        """Check if shoulders are aligned (facing camera)"""
        left_shoulder = pose_landmarks.landmark[11]
        right_shoulder = pose_landmarks.landmark[12]
        
        # Check horizontal alignment
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        
        # Check if one shoulder is significantly forward (depth)
        depth_diff = abs(left_shoulder.z - right_shoulder.z) if hasattr(left_shoulder, 'z') else 0
        
        if shoulder_diff < 0.05 and depth_diff < 0.1:
            return "aligned"
        elif depth_diff > 0.15:
            return "turned_away"
        else:
            return "slightly_misaligned"
    
    def _detect_fidgeting(self) -> bool:
        """Detect if person is fidgeting (constant movement)"""
        if len(self.shoulder_positions) < 30:
            return False
        
        variance = calculate_position_variance(list(self.shoulder_positions), window_size=30)
        
        # High variance indicates fidgeting
        return variance > self.config.POSITION_VARIANCE_THRESHOLD
    
    def _classify_posture(self, neck_angle: float, torso_angle: float,
                         is_slouching: bool, is_leaning_back: bool,
                         is_leaning_forward: bool, shoulder_alignment: str) -> Tuple[str, float]:
        """Classify overall posture"""
        
        confidence = 0.5
        
        # Poor postures (high priority)
        if is_slouching:
            return "slouching", 0.85
        
        if is_leaning_back:
            return "leaning_back", 0.80
        
        if shoulder_alignment == "turned_away":
            return "facing_away", 0.80
        
        # Good postures
        if is_leaning_forward and shoulder_alignment == "aligned":
            # Engaged, leaning in slightly
            return "engaged_forward_lean", 0.85
        
        if (self.neck_angle_good_min < neck_angle < self.neck_angle_good_max and
            self.torso_angle_good_min < torso_angle < self.torso_angle_good_max and
            shoulder_alignment == "aligned"):
            return "upright_relaxed", 0.90
        
        # Neutral postures
        if shoulder_alignment == "aligned":
            return "neutral_posture", 0.70
        
        return "slightly_poor", 0.60
    
    def _default_result(self) -> Dict:
        """Return default result when no pose detected"""
        return {
            'posture_status': 'no_pose',
            'confidence': 0.0,
            'neck_angle': 0.0,
            'torso_angle': 0.0,
            'is_slouching': False,
            'is_leaning_back': False,
            'is_leaning_forward': False,
            'shoulder_alignment': 'unknown',
            'is_fidgeting': False
        }
    
    def get_posture_quality_score(self) -> float:
        """Calculate overall posture quality (0-1)"""
        if len(self.torso_angles) < 10:
            return 0.5
        
        recent_torso = list(self.torso_angles)[-30:]
        recent_neck = list(self.neck_angles)[-30:]
        
        # Count good frames
        good_frames = sum(1 for t, n in zip(recent_torso, recent_neck)
                         if (self.torso_angle_good_min < t < self.torso_angle_good_max and
                             self.neck_angle_good_min < n < self.neck_angle_good_max))
        
        return good_frames / len(recent_torso)
