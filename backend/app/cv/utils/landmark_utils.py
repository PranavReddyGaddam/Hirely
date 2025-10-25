"""
Utility functions for landmark geometry calculations
"""

import numpy as np
import math
from typing import List, Tuple, Optional


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two 2D points"""
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


def calculate_distance_3d(point1: Tuple[float, float, float], 
                         point2: Tuple[float, float, float]) -> float:
    """Calculate Euclidean distance between two 3D points"""
    return math.sqrt(
        (point2[0] - point1[0])**2 + 
        (point2[1] - point1[1])**2 + 
        (point2[2] - point1[2])**2
    )


def calculate_angle(point1: Tuple[float, float], 
                   point2: Tuple[float, float], 
                   point3: Tuple[float, float]) -> float:
    """
    Calculate angle at point2 formed by point1-point2-point3
    Returns angle in degrees
    """
    # Create vectors
    vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    
    # Calculate angle using dot product
    cos_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    
    return np.degrees(angle)


def calculate_angle_vertical(point1: Tuple[float, float], 
                             point2: Tuple[float, float]) -> float:
    """
    Calculate angle of line (point1->point2) with respect to vertical axis
    Returns angle in degrees
    """
    # Vector from point1 to point2
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    
    # Angle with vertical (y-axis)
    # Using atan2 for proper quadrant handling
    angle = math.atan2(abs(dx), abs(dy))
    
    return math.degrees(angle)


def calculate_eye_aspect_ratio(eye_landmarks: List[Tuple[float, float]]) -> float:
    """
    Calculate Eye Aspect Ratio (EAR)
    eye_landmarks: 6 points in order [outer, top1, top2, inner, bottom2, bottom1]
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    """
    if len(eye_landmarks) != 6:
        return 0.0
    
    # Vertical distances
    vertical1 = calculate_distance(eye_landmarks[1], eye_landmarks[5])
    vertical2 = calculate_distance(eye_landmarks[2], eye_landmarks[4])
    
    # Horizontal distance
    horizontal = calculate_distance(eye_landmarks[0], eye_landmarks[3])
    
    # Calculate EAR
    ear = (vertical1 + vertical2) / (2.0 * horizontal + 1e-6)
    
    return ear


def calculate_mouth_aspect_ratio(mouth_landmarks: List[Tuple[float, float]]) -> float:
    """
    Calculate Mouth Aspect Ratio (MAR)
    mouth_landmarks: 8 key points [left, top1, top2, right, bottom2, bottom1, width_ref1, width_ref2]
    MAR = (vertical distances) / (horizontal distance)
    """
    if len(mouth_landmarks) < 6:
        return 0.0
    
    # Vertical distances (multiple points for better accuracy)
    vertical1 = calculate_distance(mouth_landmarks[1], mouth_landmarks[5])
    vertical2 = calculate_distance(mouth_landmarks[2], mouth_landmarks[4])
    
    # Horizontal distance
    horizontal = calculate_distance(mouth_landmarks[0], mouth_landmarks[3])
    
    # Calculate MAR
    mar = (vertical1 + vertical2) / (2.0 * horizontal + 1e-6)
    
    return mar


def calculate_lip_distance(upper_lip: Tuple[float, float], 
                          lower_lip: Tuple[float, float]) -> float:
    """Calculate distance between upper and lower lip (for detecting pursing/biting)"""
    return calculate_distance(upper_lip, lower_lip)


def calculate_mouth_width(left_corner: Tuple[float, float], 
                         right_corner: Tuple[float, float]) -> float:
    """Calculate mouth width"""
    return calculate_distance(left_corner, right_corner)


def calculate_eyebrow_position(eyebrow_points: List[Tuple[float, float]], 
                               eye_points: List[Tuple[float, float]]) -> float:
    """
    Calculate average distance between eyebrow and eye
    Higher values = raised eyebrows, lower = lowered/furrowed
    """
    if not eyebrow_points or not eye_points:
        return 0.0
    
    # Calculate average y-position of eyebrow and eye
    eyebrow_y = np.mean([p[1] for p in eyebrow_points])
    eye_y = np.mean([p[1] for p in eye_points])
    
    # Distance (note: y increases downward in image coordinates)
    distance = abs(eyebrow_y - eye_y)
    
    return distance


def calculate_face_direction(nose: Tuple[float, float], 
                             left_ear: Tuple[float, float], 
                             right_ear: Tuple[float, float],
                             image_center_x: float) -> Tuple[float, str]:
    """
    Calculate face direction/orientation
    Returns (angle_offset, direction_label)
    """
    # Calculate horizontal offset from center
    nose_offset = nose[0] - image_center_x
    
    # Calculate ear visibility (asymmetry indicates head turn)
    nose_to_left = abs(nose[0] - left_ear[0]) if left_ear[0] > 0 else 0
    nose_to_right = abs(nose[0] - right_ear[0]) if right_ear[0] > 0 else 0
    
    # Determine direction
    if abs(nose_offset) < image_center_x * 0.1:
        direction = "center"
        angle = 0
    elif nose_to_left > nose_to_right * 1.5:
        direction = "left"
        angle = -30
    elif nose_to_right > nose_to_left * 1.5:
        direction = "right"
        angle = 30
    else:
        direction = "center"
        angle = nose_offset / image_center_x * 20  # Approximate angle
    
    return angle, direction


def calculate_head_pose(nose: Tuple[float, float], 
                       chin: Tuple[float, float],
                       left_eye: Tuple[float, float],
                       right_eye: Tuple[float, float]) -> Tuple[float, float]:
    """
    Calculate head pose angles (pitch and yaw approximation)
    Returns (pitch, yaw) in degrees
    """
    # Pitch (up/down): angle of nose-chin line from vertical
    pitch = calculate_angle_vertical(nose, chin)
    
    # Yaw (left/right): asymmetry in eye positions
    eye_center_x = (left_eye[0] + right_eye[0]) / 2
    nose_offset = nose[0] - eye_center_x
    eye_distance = calculate_distance(left_eye, right_eye)
    
    # Normalize and convert to approximate yaw angle
    yaw = (nose_offset / (eye_distance + 1e-6)) * 45  # Approximate scaling
    
    return pitch, yaw


def calculate_smile_intensity(mouth_corners: Tuple[Tuple[float, float], Tuple[float, float]],
                              mouth_top: Tuple[float, float],
                              mouth_bottom: Tuple[float, float]) -> float:
    """
    Calculate smile intensity based on mouth corner elevation and width
    Returns value between 0 (neutral) and 1 (full smile)
    """
    left_corner, right_corner = mouth_corners
    
    # Calculate mouth width
    width = calculate_distance(left_corner, right_corner)
    
    # Calculate mouth height
    height = calculate_distance(mouth_top, mouth_bottom)
    
    # Calculate corner elevation (how much corners are raised)
    # Average y-position of corners vs bottom
    corners_y = (left_corner[1] + right_corner[1]) / 2
    elevation = abs(corners_y - mouth_bottom[1])
    
    # Smile intensity: combination of width/height ratio and elevation
    ratio = width / (height + 1e-6)
    intensity = min(1.0, (ratio - 2.0) / 3.0 + elevation * 2.0)
    
    return max(0.0, intensity)


def calculate_position_variance(positions: List[Tuple[float, float]], 
                               window_size: int = 30) -> float:
    """
    Calculate variance in position over time window (for fidgeting detection)
    """
    if len(positions) < 2:
        return 0.0
    
    recent_positions = positions[-window_size:]
    
    # Calculate variance in x and y
    x_coords = [p[0] for p in recent_positions]
    y_coords = [p[1] for p in recent_positions]
    
    variance = np.var(x_coords) + np.var(y_coords)
    
    return variance


def calculate_hand_velocity(positions: List[Tuple[float, float]], 
                           fps: int = 30) -> float:
    """
    Calculate average hand velocity (for gesture detection)
    """
    if len(positions) < 2:
        return 0.0
    
    # Calculate distance moved per frame
    distances = []
    for i in range(1, len(positions)):
        dist = calculate_distance(positions[i-1], positions[i])
        distances.append(dist)
    
    # Average velocity
    avg_velocity = np.mean(distances) if distances else 0.0
    
    return avg_velocity * fps  # Convert to per-second


def is_hand_near_face(hand_landmarks: List[Tuple[float, float]], 
                     face_landmarks: List[Tuple[float, float]],
                     threshold: float = 0.1) -> bool:
    """
    Check if hand is near face (for face-touching detection)
    """
    if not hand_landmarks or not face_landmarks:
        return False
    
    # Get hand center (wrist or palm)
    hand_center = hand_landmarks[0] if hand_landmarks else (0, 0)
    
    # Check distance to face landmarks
    for face_point in face_landmarks:
        dist = calculate_distance(hand_center, face_point)
        if dist < threshold:
            return True
    
    return False


def normalize_landmarks(landmarks, image_width: int, image_height: int) -> List[Tuple[float, float]]:
    """
    Normalize landmarks to 0-1 range based on image dimensions
    """
    normalized = []
    for lm in landmarks:
        x = lm.x if hasattr(lm, 'x') else lm[0]
        y = lm.y if hasattr(lm, 'y') else lm[1]
        normalized.append((x, y))
    
    return normalized


def get_landmark_subset(all_landmarks: List[Tuple[float, float]], 
                       indices: List[int]) -> List[Tuple[float, float]]:
    """
    Extract subset of landmarks based on indices
    """
    return [all_landmarks[i] for i in indices if i < len(all_landmarks)]


def smooth_value(current_value: float, 
                previous_value: float, 
                smoothing_factor: float = 0.7) -> float:
    """
    Apply exponential smoothing to reduce jitter
    smoothing_factor: 0-1, higher = more smoothing
    """
    return smoothing_factor * previous_value + (1 - smoothing_factor) * current_value


def calculate_landmark_center(landmarks: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate center point of a set of landmarks"""
    if not landmarks:
        return (0, 0)
    
    x_coords = [p[0] for p in landmarks]
    y_coords = [p[1] for p in landmarks]
    
    return (np.mean(x_coords), np.mean(y_coords))
