"""
Head Pose Estimation Module
Real-time estimation of head orientation (yaw, pitch, roll) using MediaPipe
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Optional
import mediapipe as mp


class HeadPoseEstimator:
    """
    Estimates head pose (yaw, pitch, roll) from MediaPipe face landmarks.
    Based on 2024-2025 best practices for attention/gaze tracking.
    """
    
    def __init__(self):
        # 3D model points for key facial features
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype="double")
        
        # Camera internals (will be set dynamically)
        self.focal_length = 1.0
        self.camera_matrix = None
        self.dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        
        print("[HeadPose] Initialized with 6-point 3D model")
    
    def update_camera_matrix(self, width: int, height: int):
        """Update camera matrix based on frame dimensions"""
        self.focal_length = width
        center = (width / 2, height / 2)
        self.camera_matrix = np.array([
            [self.focal_length, 0, center[0]],
            [0, self.focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
    
    def estimate(self, face_landmarks, image_width: int, image_height: int) -> Dict:
        """
        Estimate head pose from MediaPipe face landmarks.
        
        Returns:
            Dict with yaw, pitch, roll angles and direction status
        """
        if not face_landmarks:
            return self._default_result()
        
        # Update camera matrix if dimensions changed
        if self.camera_matrix is None:
            self.update_camera_matrix(image_width, image_height)
        
        # Extract 2D image points for the 6 key landmarks
        image_points = np.array([
            self._get_landmark_point(face_landmarks, 1, image_width, image_height),    # Nose tip
            self._get_landmark_point(face_landmarks, 152, image_width, image_height),  # Chin
            self._get_landmark_point(face_landmarks, 33, image_width, image_height),   # Left eye left corner
            self._get_landmark_point(face_landmarks, 263, image_width, image_height),  # Right eye right corner
            self._get_landmark_point(face_landmarks, 61, image_width, image_height),   # Left mouth corner
            self._get_landmark_point(face_landmarks, 291, image_width, image_height)   # Right mouth corner
        ], dtype="double")
        
        # Solve PnP to get rotation and translation vectors
        success, rotation_vec, translation_vec = cv2.solvePnP(
            self.model_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return self._default_result()
        
        # Convert rotation vector to rotation matrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        
        # Calculate Euler angles (yaw, pitch, roll)
        yaw, pitch, roll = self._rotation_matrix_to_euler_angles(rotation_mat)
        
        # Determine direction based on yaw angle
        direction = self._get_direction(yaw, pitch)
        
        # Calculate engagement score (0-1)
        engagement_score = self._calculate_engagement(yaw, pitch, roll)
        
        return {
            'head_yaw': yaw,
            'head_pitch': pitch,
            'head_roll': roll,
            'head_direction': direction,
            'engagement_score': engagement_score,
            'is_looking_at_camera': abs(yaw) < 15 and abs(pitch) < 15,
            'is_looking_away': abs(yaw) > 30 or abs(pitch) > 25,
            'rotation_vec': rotation_vec,
            'translation_vec': translation_vec
        }
    
    def _get_landmark_point(self, face_landmarks, index: int, 
                           width: int, height: int) -> Tuple[float, float]:
        """Extract 2D coordinates of a specific landmark"""
        landmark = face_landmarks.landmark[index]
        return (landmark.x * width, landmark.y * height)
    
    def _rotation_matrix_to_euler_angles(self, R: np.ndarray) -> Tuple[float, float, float]:
        """
        Convert rotation matrix to Euler angles (yaw, pitch, roll).
        Returns angles in degrees.
        """
        # Calculate pitch
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6
        
        if not singular:
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = np.arctan2(R[1, 0], R[0, 0])
            roll = np.arctan2(R[2, 1], R[2, 2])
        else:
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = np.arctan2(-R[1, 2], R[1, 1])
            roll = 0
        
        # Convert from radians to degrees
        pitch = np.degrees(pitch)
        yaw = np.degrees(yaw)
        roll = np.degrees(roll)
        
        return yaw, pitch, roll
    
    def _get_direction(self, yaw: float, pitch: float) -> str:
        """
        Determine head direction from yaw and pitch angles.
        
        Yaw: Left (-) / Right (+)
        Pitch: Down (-) / Up (+)
        """
        # Primary direction based on yaw
        if abs(yaw) < 15 and abs(pitch) < 15:
            return "center"
        elif yaw < -20:
            return "left"
        elif yaw > 20:
            return "right"
        elif pitch < -15:
            return "down"
        elif pitch > 15:
            return "up"
        else:
            return "center"
    
    def _calculate_engagement(self, yaw: float, pitch: float, roll: float) -> float:
        """
        Calculate engagement score based on head orientation.
        Perfect center = 1.0, extreme angles = 0.0
        
        More lenient calculation - normal conversation has some head movement.
        """
        # Penalize based on angle deviation (more lenient ranges)
        yaw_penalty = max(0.0, (abs(yaw) - 15) / 75.0)  # Start penalizing after 15°
        pitch_penalty = max(0.0, (abs(pitch) - 15) / 45.0)  # Start penalizing after 15°
        roll_penalty = max(0.0, (abs(roll) - 10) / 35.0)  # Start penalizing after 10°
        
        # Combined penalty (less weight on roll - head tilt is natural)
        total_penalty = (yaw_penalty * 0.6 + pitch_penalty * 0.3 + roll_penalty * 0.1)
        
        # Engagement score (inverted penalty) - minimum 0.3 to avoid false alerts
        engagement = max(0.3, 1.0 - total_penalty)
        
        return engagement
    
    def _default_result(self) -> Dict:
        """Return default result when estimation fails"""
        return {
            'head_yaw': 0.0,
            'head_pitch': 0.0,
            'head_roll': 0.0,
            'head_direction': 'center',  # Assume center when unknown (benefit of doubt)
            'engagement_score': 0.7,  # Default to reasonable score (not 0.0 which triggers alerts)
            'is_looking_at_camera': True,  # Assume looking when unknown
            'is_looking_away': False,
            'rotation_vec': None,
            'translation_vec': None
        }
    
    def visualize_axes(self, frame: np.ndarray, face_landmarks, 
                       image_width: int, image_height: int, 
                       result: Dict) -> np.ndarray:
        """
        Draw 3D coordinate axes on the frame to visualize head pose.
        """
        if result['rotation_vec'] is None:
            return frame
        
        # Get nose tip as origin
        nose_tip = self._get_landmark_point(face_landmarks, 1, image_width, image_height)
        
        # Define 3D axis points
        axis = np.float32([
            [500, 0, 0],    # X axis (red) - right
            [0, 500, 0],    # Y axis (green) - down
            [0, 0, -500]    # Z axis (blue) - forward
        ])
        
        # Project 3D points to 2D
        imgpts, _ = cv2.projectPoints(
            axis, 
            result['rotation_vec'], 
            result['translation_vec'],
            self.camera_matrix, 
            self.dist_coeffs
        )
        
        # Draw axes
        nose_tip = tuple(np.int32(nose_tip))
        imgpts = np.int32(imgpts).reshape(-1, 2)
        
        # X axis (red) - right
        frame = cv2.line(frame, nose_tip, tuple(imgpts[0]), (0, 0, 255), 3)
        # Y axis (green) - down
        frame = cv2.line(frame, nose_tip, tuple(imgpts[1]), (0, 255, 0), 3)
        # Z axis (blue) - forward (towards camera)
        frame = cv2.line(frame, nose_tip, tuple(imgpts[2]), (255, 0, 0), 3)
        
        return frame
