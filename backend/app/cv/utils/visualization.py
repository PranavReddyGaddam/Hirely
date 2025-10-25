"""
Visualization utilities for rendering landmarks and UI elements
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import mediapipe as mp


class Visualizer:
    """Handles all visualization and rendering"""
    
    def __init__(self, config):
        self.config = config
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Colors
        self.COLOR_GOOD = config.COLOR_GOOD
        self.COLOR_NEUTRAL = config.COLOR_NEUTRAL
        self.COLOR_BAD = config.COLOR_BAD
        self.COLOR_BLUE = config.COLOR_BLUE
        self.COLOR_WHITE = config.COLOR_WHITE
        self.COLOR_BLACK = config.COLOR_BLACK
        
    def draw_normal_mode(self, 
                        frame: np.ndarray,
                        expression: str,
                        expression_confidence: float,
                        posture_status: str,
                        attention_score: float,
                        alerts: List[str],
                        is_calibrating: bool = False,
                        calibration_progress: float = 0.0) -> np.ndarray:
        """Draw normal mode visualization"""
        
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Draw semi-transparent overlay for text background
        cv2.rectangle(overlay, (10, 10), (w-10, 150), self.COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Calibration mode
        if is_calibrating:
            self._draw_calibration_overlay(frame, calibration_progress)
            return frame
        
        # Expression (top-left)
        expression_color = self._get_expression_color(expression)
        cv2.putText(frame, f"Expression: {expression}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, expression_color, 2)
        cv2.putText(frame, f"Confidence: {expression_confidence:.2f}", 
                   (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, self.COLOR_WHITE, 1)
        
        # Posture (top-right)
        posture_color = self._get_posture_color(posture_status)
        text_size = cv2.getTextSize(f"Posture: {posture_status}", 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cv2.putText(frame, f"Posture: {posture_status}", 
                   (w - text_size[0] - 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, posture_color, 2)
        
        # Attention score bar (bottom center)
        self._draw_attention_bar(frame, attention_score)
        
        # Alerts (top center, below header)
        if alerts:
            self._draw_alerts(frame, alerts)
        
        return frame
    
    def draw_skeleton_mode(self,
                          frame: np.ndarray,
                          face_landmarks,
                          pose_landmarks,
                          hand_landmarks_list,
                          skeleton_density: float,
                          attention_score: float,
                          is_calibrating: bool = False,
                          calibration_progress: float = 0.0) -> np.ndarray:
        """Draw skeleton mode with adjustable density"""
        
        if is_calibrating:
            self._draw_calibration_overlay(frame, calibration_progress)
            return frame
        
        h, w = frame.shape[:2]
        
        # Determine number of landmarks to show based on density
        density_percent = skeleton_density / 100.0
        
        # Draw face mesh
        if face_landmarks:
            self._draw_face_landmarks(frame, face_landmarks, density_percent)
        
        # Draw pose
        if pose_landmarks:
            self._draw_pose_landmarks(frame, pose_landmarks, density_percent)
        
        # Draw hands
        if hand_landmarks_list:
            for hand_landmarks in hand_landmarks_list:
                self._draw_hand_landmarks(frame, hand_landmarks, density_percent)
        
        # Draw density indicator
        cv2.putText(frame, f"Skeleton Density: {int(skeleton_density)}%", 
                   (20, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, self.COLOR_WHITE, 2)
        
        # Attention score bar
        self._draw_attention_bar(frame, attention_score)
        
        return frame
    
    def _draw_face_landmarks(self, frame: np.ndarray, landmarks, density: float):
        """Draw face landmarks based on density"""
        h, w = frame.shape[:2]
        
        if density < 0.3:
            # Low density: only key points (eyes, nose, mouth corners)
            key_indices = [33, 133, 362, 263, 1, 61, 291, 0, 17]  # ~10 points
            self._draw_landmark_points(frame, landmarks, key_indices, self.COLOR_BLUE, 3)
        
        elif density < 0.7:
            # Medium density: face contours
            mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=self.COLOR_BLUE, thickness=1, circle_radius=1),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=self.COLOR_BLUE, thickness=1)
            )
        
        else:
            # High density: full mesh
            mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=self.COLOR_BLUE, thickness=1)
            )
    
    def _draw_pose_landmarks(self, frame: np.ndarray, landmarks, density: float):
        """Draw pose landmarks based on density"""
        mp_pose = mp.solutions.pose
        
        if density < 0.3:
            # Low density: only torso and head
            connections = [
                (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
                (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP),
                (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
            ]
            self._draw_custom_connections(frame, landmarks, connections, (0, 255, 0))
        
        else:
            # Medium/High density: full skeleton
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=3),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=2)
            )
    
    def _draw_hand_landmarks(self, frame: np.ndarray, landmarks, density: float):
        """Draw hand landmarks based on density"""
        mp_hands = mp.solutions.hands
        
        if density < 0.3:
            # Low density: only fingertips and wrist
            key_indices = [0, 4, 8, 12, 16, 20]
            self._draw_landmark_points(frame, landmarks, key_indices, (0, 255, 255), 4)
        
        else:
            # Medium/High density: full hand skeleton
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 255), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 255), thickness=2)
            )
    
    def _draw_landmark_points(self, frame, landmarks, indices, color, radius):
        """Draw specific landmark points"""
        h, w = frame.shape[:2]
        for idx in indices:
            if idx < len(landmarks.landmark):
                lm = landmarks.landmark[idx]
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), radius, color, -1)
    
    def _draw_custom_connections(self, frame, landmarks, connections, color):
        """Draw custom connections between landmarks"""
        h, w = frame.shape[:2]
        for connection in connections:
            start_idx = connection[0].value if hasattr(connection[0], 'value') else connection[0]
            end_idx = connection[1].value if hasattr(connection[1], 'value') else connection[1]
            
            if start_idx < len(landmarks.landmark) and end_idx < len(landmarks.landmark):
                start_lm = landmarks.landmark[start_idx]
                end_lm = landmarks.landmark[end_idx]
                
                start_point = (int(start_lm.x * w), int(start_lm.y * h))
                end_point = (int(end_lm.x * w), int(end_lm.y * h))
                
                cv2.line(frame, start_point, end_point, color, 2)
                cv2.circle(frame, start_point, 4, color, -1)
                cv2.circle(frame, end_point, 4, color, -1)
    
    def _draw_attention_bar(self, frame: np.ndarray, attention_score: float):
        """Draw attention score progress bar"""
        h, w = frame.shape[:2]
        
        bar_width = 400
        bar_height = 30
        bar_x = (w - bar_width) // 2
        bar_y = h - 50
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     self.COLOR_BLACK, -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     self.COLOR_WHITE, 2)
        
        # Fill based on score
        fill_width = int(bar_width * attention_score)
        color = self.COLOR_GOOD if attention_score > 0.7 else \
                self.COLOR_NEUTRAL if attention_score > 0.4 else \
                self.COLOR_BAD
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                     color, -1)
        
        # Text
        text = f"Attention: {int(attention_score * 100)}%"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        text_y = bar_y + (bar_height + text_size[1]) // 2
        
        cv2.putText(frame, text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_WHITE, 2)
    
    def _draw_alerts(self, frame: np.ndarray, alerts: List[str]):
        """Draw alert messages"""
        h, w = frame.shape[:2]
        
        y_offset = 100
        for alert in alerts:
            # Background
            text_size = cv2.getTextSize(alert, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            x_center = (w - text_size[0]) // 2
            
            cv2.rectangle(frame, 
                         (x_center - 10, y_offset - 35), 
                         (x_center + text_size[0] + 10, y_offset + 5), 
                         self.COLOR_BAD, -1)
            cv2.rectangle(frame, 
                         (x_center - 10, y_offset - 35), 
                         (x_center + text_size[0] + 10, y_offset + 5), 
                         self.COLOR_WHITE, 2)
            
            # Text
            cv2.putText(frame, alert, (x_center, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_WHITE, 2)
            
            y_offset += 50
    
    def _draw_calibration_overlay(self, frame: np.ndarray, progress: float):
        """Draw calibration overlay"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), self.COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Title
        title = "CALIBRATION IN PROGRESS"
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        cv2.putText(frame, title, 
                   ((w - title_size[0]) // 2, h // 2 - 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.COLOR_WHITE, 3)
        
        # Instructions
        instructions = [
            "Please sit in good posture",
            "Look at the camera",
            "Stay still for calibration"
        ]
        
        y_offset = h // 2 - 20
        for instruction in instructions:
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.putText(frame, instruction, 
                       ((w - text_size[0]) // 2, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_NEUTRAL, 2)
            y_offset += 40
        
        # Progress bar
        bar_width = 500
        bar_height = 40
        bar_x = (w - bar_width) // 2
        bar_y = h // 2 + 80
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     self.COLOR_WHITE, 3)
        
        fill_width = int(bar_width * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                     self.COLOR_GOOD, -1)
        
        # Progress text
        progress_text = f"{int(progress * 100)}%"
        text_size = cv2.getTextSize(progress_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        cv2.putText(frame, progress_text, 
                   ((w - text_size[0]) // 2, bar_y + bar_height + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.COLOR_WHITE, 2)
    
    def _get_expression_color(self, expression: str) -> Tuple[int, int, int]:
        """Get color for expression"""
        positive_expressions = ['genuine_smile', 'attentive', 'calm', 'happy']
        negative_expressions = ['frowning', 'sleepy', 'not_focusing', 'blank', 'tense']
        
        if expression.lower() in positive_expressions:
            return self.COLOR_GOOD
        elif expression.lower() in negative_expressions:
            return self.COLOR_BAD
        else:
            return self.COLOR_NEUTRAL
    
    def _get_posture_color(self, posture: str) -> Tuple[int, int, int]:
        """Get color for posture"""
        good_postures = ['upright', 'engaged', 'good']
        bad_postures = ['slouching', 'leaning_back', 'poor', 'bad']
        
        if any(good in posture.lower() for good in good_postures):
            return self.COLOR_GOOD
        elif any(bad in posture.lower() for bad in bad_postures):
            return self.COLOR_BAD
        else:
            return self.COLOR_NEUTRAL
