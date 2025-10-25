"""
CV Processor Service
Wrapper around CV copy detectors for real-time interview analysis
Processes frames from frontend and returns behavioral metrics
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Optional
import time
from datetime import datetime

from app.cv.detectors.face_expression_deepface import DeepFaceExpressionDetector
from app.cv.detectors.head_pose_estimator import HeadPoseEstimator
from app.cv.detectors.posture_analyzer import PostureAnalyzer
from app.cv.detectors.gesture_detector import GestureDetector
from app.cv.detectors.attention_tracker import AttentionTracker
from app.cv.utils.data_logger import DataLogger
from app.cv.config import settings as cv_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CVProcessor:
    """
    CV Processor - integrates all CV copy detectors
    Processes frames from frontend and returns real-time metrics
    """
    
    def __init__(self):
        """Initialize all CV components (same as cv copy/main.py)"""
        
        logger.info("[CVProcessor] Initializing MediaPipe and detectors...")
        
        # Initialize MediaPipe (exact same as CV copy)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=cv_config.FACE_MESH_MAX_FACES,
            refine_landmarks=cv_config.FACE_MESH_REFINE_LANDMARKS,
            min_detection_confidence=cv_config.FACE_MESH_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=cv_config.FACE_MESH_MIN_TRACKING_CONFIDENCE
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=cv_config.POSE_MODEL_COMPLEXITY,
            smooth_landmarks=cv_config.POSE_SMOOTH_LANDMARKS,
            min_detection_confidence=cv_config.POSE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=cv_config.POSE_MIN_TRACKING_CONFIDENCE
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=cv_config.HANDS_MAX_NUM_HANDS,
            min_detection_confidence=cv_config.HANDS_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=cv_config.HANDS_MIN_TRACKING_CONFIDENCE
        )
        
        # Initialize detectors (exact same as CV copy)
        logger.info("[CVProcessor] Initializing detectors...")
        self.face_detector = DeepFaceExpressionDetector(cv_config)
        self.posture_analyzer = PostureAnalyzer(cv_config)
        self.gesture_detector = GestureDetector(cv_config)
        self.attention_tracker = AttentionTracker(cv_config)
        self.head_pose = HeadPoseEstimator()
        
        # Data logger
        self.data_logger = DataLogger(buffer_size=cv_config.BUFFER_SIZE)
        
        # Session state
        self.session_active = False
        self.frame_count = 0
        self.session_start_time = None
        
        logger.info("[CVProcessor] Initialization complete!")
    
    def start_session(self) -> Dict:
        """Start new CV tracking session"""
        logger.info("[CVProcessor] Starting new session...")
        
        self.data_logger.start_session()
        self.session_active = True
        self.frame_count = 0
        self.session_start_time = time.time()
        
        return {
            "status": "started",
            "session_id": self.data_logger.session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_frame(self, frame_bytes: bytes) -> Dict:
        """
        Process single frame - EXACT same logic as cv copy/main.py
        
        Args:
            frame_bytes: JPEG encoded frame from frontend
            
        Returns:
            Dict with all 27 behavioral metrics
        """
        
        if not self.session_active:
            logger.warning("[CVProcessor] Session not active, call start_session() first")
            return self._default_metrics()
        
        try:
            # Decode JPEG bytes to numpy array
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("[CVProcessor] Failed to decode frame")
                return self._default_metrics()
            
            # Get frame dimensions
            h, w, _ = frame.shape
            
            # Convert BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe (same as CV copy)
            face_results = self.face_mesh.process(frame_rgb)
            pose_results = self.pose.process(frame_rgb)
            hand_results = self.hands.process(frame_rgb)
            
            # Calculate elapsed time
            elapsed_time = time.time() - self.session_start_time
            
            # Initialize metrics dict
            metrics = {
                'frame_number': self.frame_count,
                'elapsed_seconds': elapsed_time
            }
            
            # Process face (expression + head pose)
            expression_data = {}
            head_pose_data = {}
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                logger.info(f"[CVProcessor] ✅ Face detected! Processing frame {self.frame_count}")
                
                # Face expression detection (DeepFace)
                expression_data = self.face_detector.detect(
                    face_landmarks,
                    w, h,
                    frame=frame,
                    timestamp=elapsed_time
                )
                metrics.update(expression_data)
                
                # Head pose estimation
                head_pose_data = self.head_pose.estimate(face_landmarks, w, h)
                metrics.update(head_pose_data)
                
                # Mark face as detected
                metrics['face_detected'] = True
            else:
                # No face detected - use defaults
                logger.warning(f"[CVProcessor] NO FACE DETECTED in frame {self.frame_count}! Check camera/lighting")
                expression_data = self._default_face_metrics()
                head_pose_data = {}
                metrics.update(expression_data)
                # Add flag to indicate no face detected
                metrics['face_detected'] = False
            
            # Process posture
            posture_data = {}
            if pose_results.pose_landmarks:
                posture_data = self.posture_analyzer.analyze(
                    pose_results.pose_landmarks
                )
                metrics.update(posture_data)
            else:
                posture_data = self._default_posture_metrics()
                metrics.update(posture_data)
            
            # Process hand gestures
            gesture_data = {}
            if hand_results.multi_hand_landmarks:
                gesture_data = self.gesture_detector.detect_gestures(
                    hand_results.multi_hand_landmarks,
                    face_results.multi_face_landmarks if face_results.multi_face_landmarks else None
                )
                metrics.update(gesture_data)
            else:
                gesture_data = self._default_gesture_metrics()
                metrics.update(gesture_data)
            
            # Calculate attention score (combines all metrics)
            attention_data = self.attention_tracker.calculate_attention(
                expression_data,
                posture_data,
                gesture_data,
                head_pose_data=head_pose_data
            )
            metrics.update(attention_data)
            
            # Log to data buffer
            self.data_logger.log_frame_data(metrics)
            self.frame_count += 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"[CVProcessor] Error processing frame: {e}", exc_info=True)
            return self._default_metrics()
    
    def stop_session(self, export_path: str = "exports") -> Dict:
        """
        Stop session and generate analysis (same as CV copy)
        
        Returns:
            Dict with export file paths and analysis data
        """
        logger.info("[CVProcessor] Stopping session and generating exports...")
        
        if not self.session_active:
            logger.warning("[CVProcessor] No active session to stop")
            return {}
        
        try:
            # Generate exports (exact same as CV copy)
            export_files = self.data_logger.export_all(output_dir=export_path)
            
            self.session_active = False
            
            logger.info(f"[CVProcessor] Session stopped. Exports saved to: {export_path}")
            
            return {
                "status": "stopped",
                "export_files": export_files,
                "total_frames": self.frame_count,
                "duration_seconds": time.time() - self.session_start_time
            }
            
        except Exception as e:
            logger.error(f"[CVProcessor] Error stopping session: {e}", exc_info=True)
            self.session_active = False
            return {"status": "error", "message": str(e)}
    
    def _default_metrics(self) -> Dict:
        """Return default metrics when processing fails"""
        return {
            'expression': 'calm',
            'confidence': 0.0,
            'ear_left': 0.0,
            'ear_right': 0.0,
            'ear_avg': 0.0,
            'mar': 0.0,
            'smile_intensity': 0.0,
            'is_blinking': False,
            'blink_count': 0,
            'blink_rate': 0.0,
            'stress_level': 'unknown',
            'head_yaw': 0.0,
            'head_pitch': 0.0,
            'head_roll': 0.0,
            'head_direction': 'center',
            'is_looking_at_camera': False,
            'posture_status': 'unknown',
            'neck_angle': 0.0,
            'torso_angle': 0.0,
            'is_slouching': False,
            'face_touching': False,
            'hand_fidgeting': False,
            'excessive_gesturing': False,
            'face_touch_count': 0,
            'attention_score': 0.0,
            'is_engaged': False,
            'is_distracted': False,
            'alert_count': 0
        }
    
    def _default_face_metrics(self) -> Dict:
        """Default metrics when no face detected"""
        return {
            'expression': 'calm',
            'confidence': 0.0,
            'expression_confidence': 0.0,
            'ear_left': 0.0,
            'ear_right': 0.0,
            'ear_avg': 0.0,
            'mar': 0.0,
            'smile_intensity': 0.0,
            'is_blinking': False,
            'blink_count': 0,
            'blink_rate': 0.0,
            'stress_level': 'unknown',
            'head_yaw': 0.0,
            'head_pitch': 0.0,
            'head_roll': 0.0,
            'head_direction': 'center',
            'is_looking_at_camera': False
        }
    
    def _default_posture_metrics(self) -> Dict:
        """Default metrics when no pose detected"""
        return {
            'posture_status': 'unknown',
            'neck_angle': 0.0,
            'torso_angle': 0.0,
            'is_slouching': False,
            'is_fidgeting_body': False
        }
    
    def _default_gesture_metrics(self) -> Dict:
        """Default metrics when no hands detected"""
        return {
            'face_touching': False,
            'hand_fidgeting': False,
            'excessive_gesturing': False,
            'face_touch_count': 0
        }
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("[CVProcessor] Cleaning up resources...")
        
        if self.face_mesh:
            self.face_mesh.close()
        if self.pose:
            self.pose.close()
        if self.hands:
            self.hands.close()
        
        logger.info("[CVProcessor] Cleanup complete")
