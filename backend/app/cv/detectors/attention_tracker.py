"""
Attention Tracking Module
Aggregates data from all detectors to calculate attention metrics
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque


class AttentionTracker:
    """Tracks overall attention and engagement metrics"""
    
    def __init__(self, config):
        self.config = config
        
        # Thresholds
        self.gaze_center_threshold = config.GAZE_CENTER_THRESHOLD
        self.attention_lost_frames = config.ATTENTION_LOST_FRAMES
        
        # History
        self.attention_scores = deque(maxlen=300)  # 10 seconds
        self.not_focusing_frames = 0
        self.good_posture_frames = 0
        self.total_frames = 0
        
        # Alert tracking
        self.poor_posture_consecutive = 0
        self.not_focusing_consecutive = 0
        self.fidgeting_consecutive = 0
        
    def calculate_attention(self, 
                          expression_data: Dict,
                          posture_data: Dict,
                          gesture_data: Dict,
                          face_direction: Tuple[float, str] = None,
                          head_pose_data: Dict = None) -> Dict:
        """
        Calculate overall attention score and generate alerts
        """
        self.total_frames += 1
        
        # Component scores (0-1)
        expression_score = self._score_expression(expression_data)
        posture_score = self._score_posture(posture_data)
        gesture_score = self._score_gestures(gesture_data)
        
        # Use head pose data if available, otherwise fall back to face direction
        if head_pose_data and head_pose_data.get('engagement_score') is not None:
            gaze_score = head_pose_data['engagement_score']
        else:
            gaze_score = self._score_gaze(face_direction)
        
        # Weighted attention score (updated weights based on 2024-2025 research)
        # Eye contact/gaze is #1 indicator (30%), posture 30%, expression 25%, gestures 15%
        attention_score = (
            expression_score * 0.25 +
            posture_score * 0.30 +
            gesture_score * 0.15 +
            gaze_score * 0.30
        )
        
        self.attention_scores.append(attention_score)
        
        # Track consecutive poor behavior
        if posture_data.get('is_slouching') or posture_data.get('is_leaning_back'):
            self.poor_posture_consecutive += 1
        else:
            self.poor_posture_consecutive = 0
            self.good_posture_frames += 1
        
        # Lower threshold to 0.3 (was 0.5) - less sensitive, fewer false positives
        if gaze_score < 0.3:
            self.not_focusing_consecutive += 1
            self.not_focusing_frames += 1
        else:
            self.not_focusing_consecutive = 0
        
        if gesture_data.get('hand_fidgeting') or gesture_data.get('face_touching'):
            self.fidgeting_consecutive += 1
        else:
            self.fidgeting_consecutive = 0
        
        # Generate alerts
        alerts = self._generate_alerts()
        
        return {
            'attention_score': attention_score,
            'expression_score': expression_score,
            'posture_score': posture_score,
            'gesture_score': gesture_score,
            'gaze_score': gaze_score,
            # head_pose_data is already merged into metrics by cv_processor, no need to nest it here
            'avg_attention': np.mean(list(self.attention_scores)) if self.attention_scores else 0.5,
            'alerts': alerts,
            'alert_count': len(alerts),
            'is_engaged': attention_score > 0.7,
            'is_distracted': attention_score < 0.4,
            'stress_level': expression_data.get('stress_level', 'unknown'),
            'blink_rate': expression_data.get('blink_rate', 0.0)
        }
    
    def _score_expression(self, expression_data: Dict) -> float:
        """Score facial expression (0-1, higher is better)"""
        expression = expression_data.get('expression', 'neutral')
        confidence = expression_data.get('confidence', 0.5)
        
        # Positive expressions
        positive = ['attentive', 'calm', 'genuine_smile', 'happy']
        # Negative expressions
        negative = ['sleepy', 'yawning', 'not_focusing', 'blank', 'frowning', 'tense']
        
        if expression in positive:
            return 0.8 + (confidence * 0.2)
        elif expression in negative:
            return 0.2 - (confidence * 0.1)
        else:
            return 0.5
    
    def _score_posture(self, posture_data: Dict) -> float:
        """Score body posture (0-1, higher is better)"""
        posture_status = posture_data.get('posture_status', 'neutral')
        
        # Good postures
        if posture_status in ['upright_relaxed', 'engaged_forward_lean']:
            return 0.9
        # Poor postures
        elif posture_status in ['slouching', 'leaning_back', 'facing_away']:
            return 0.2
        # Neutral
        else:
            return 0.6
    
    def _score_gestures(self, gesture_data: Dict) -> float:
        """Score hand gestures (0-1, higher is better)"""
        score = 1.0
        
        # Penalize negative behaviors
        if gesture_data.get('face_touching'):
            score -= 0.3
        if gesture_data.get('hand_fidgeting'):
            score -= 0.25
        if gesture_data.get('excessive_gesturing'):
            score -= 0.2
        if gesture_data.get('crossed_arms'):
            score -= 0.15
        if gesture_data.get('hand_near_head'):
            score -= 0.1
        
        return max(0.0, score)
    
    def _score_gaze(self, face_direction: Tuple[float, str] = None) -> float:
        """Score gaze direction (0-1, higher is better)"""
        if face_direction is None:
            return 0.5
        
        # Handle both tuple and dict formats
        if isinstance(face_direction, dict):
            # Extract from dict (from head pose estimator)
            angle = abs(face_direction.get('yaw', 0))
            direction = face_direction.get('direction', 'center')
        else:
            # Handle tuple format
            angle, direction = face_direction
        
        # Good: looking at camera
        if direction == "center" and abs(angle) < 15:
            return 1.0
        elif direction == "center":
            return 0.8
        # Moderate: slight turn
        elif abs(angle) < self.gaze_center_threshold:
            return 0.6
        # Poor: looking away
        else:
            return 0.2
    
    def _generate_alerts(self) -> List[str]:
        """Generate real-time alerts based on behavior"""
        alerts = []
        
        # Poor posture alert
        if self.poor_posture_consecutive >= self.config.POOR_POSTURE_ALERT_FRAMES:
            alerts.append("Poor Posture Detected!")
        
        # Not focusing alert
        if self.not_focusing_consecutive >= self.config.NOT_FOCUSING_ALERT_FRAMES:
            alerts.append("Not Focusing - Look at Camera!")
        
        # Fidgeting alert
        if self.fidgeting_consecutive >= self.config.FIDGETING_ALERT_FRAMES:
            alerts.append("Excessive Fidgeting!")
        
        return alerts
    
    def get_session_stats(self) -> Dict:
        """Get overall session statistics"""
        if self.total_frames == 0:
            return {}
        
        return {
            'total_frames': self.total_frames,
            'avg_attention': np.mean(list(self.attention_scores)) if self.attention_scores else 0.0,
            'good_posture_percentage': (self.good_posture_frames / self.total_frames) * 100,
            'focusing_percentage': ((self.total_frames - self.not_focusing_frames) / self.total_frames) * 100
        }
    
    def reset(self):
        """Reset all tracking"""
        self.attention_scores.clear()
        self.not_focusing_frames = 0
        self.good_posture_frames = 0
        self.total_frames = 0
        self.poor_posture_consecutive = 0
        self.not_focusing_consecutive = 0
        self.fidgeting_consecutive = 0
