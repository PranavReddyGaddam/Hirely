"""
Configuration settings for Interview Expression & Posture Tracker
"""

# ======================== CAMERA SETTINGS ========================
CAMERA_INDEX = 0
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
TARGET_FPS = 30

# DeepFace settings
ENABLE_DEMOGRAPHICS = False  # Set to True to enable age/gender (downloads 1GB+ models)

# ======================== MEDIAPIPE SETTINGS ========================
# Face Mesh - LOWERED for better webcam detection
FACE_MESH_MAX_FACES = 1
FACE_MESH_MIN_DETECTION_CONFIDENCE = 0.3  # Lowered from 0.5 for webcams
FACE_MESH_MIN_TRACKING_CONFIDENCE = 0.3   # Lowered from 0.5
FACE_MESH_REFINE_LANDMARKS = True

# Pose - LOWERED for better webcam detection
POSE_MODEL_COMPLEXITY = 1  # 0, 1, or 2 (balance speed/accuracy)
POSE_MIN_DETECTION_CONFIDENCE = 0.3  # Lowered from 0.5 for webcams
POSE_MIN_TRACKING_CONFIDENCE = 0.3   # Lowered from 0.5
POSE_SMOOTH_LANDMARKS = True

# Hands - LOWERED for better webcam detection
HANDS_MAX_NUM_HANDS = 2
HANDS_MIN_DETECTION_CONFIDENCE = 0.3  # Lowered from 0.5 for webcams
HANDS_MIN_TRACKING_CONFIDENCE = 0.3   # Lowered from 0.5

# ======================== EXPRESSION THRESHOLDS ========================
# Eye Aspect Ratio (EAR)
EAR_THRESHOLD_NORMAL = 0.25
EAR_THRESHOLD_SLEEPY = 0.20
EAR_THRESHOLD_SURPRISED = 0.40
BLINK_CONSECUTIVE_FRAMES = 2

# Mouth Aspect Ratio (MAR)
MAR_THRESHOLD_NEUTRAL = 0.15
MAR_THRESHOLD_SMILE = 0.30
MAR_THRESHOLD_LAUGH = 0.60
MAR_THRESHOLD_YAWN = 0.65

# Blink rate (per minute)
BLINK_RATE_NORMAL = 15
BLINK_RATE_EXCESSIVE = 25

# Gaze/Focus
GAZE_CENTER_THRESHOLD = 30  # degrees
ATTENTION_LOST_FRAMES = 60  # 2 seconds at 30fps

# ======================== POSTURE THRESHOLDS ========================
# Neck angle (degrees)
NECK_ANGLE_GOOD_MIN = 10
NECK_ANGLE_GOOD_MAX = 30
NECK_ANGLE_BAD = 45

# Torso angle (degrees)
TORSO_ANGLE_GOOD_MIN = 5
TORSO_ANGLE_GOOD_MAX = 20
TORSO_ANGLE_SLOUCH = 35
TORSO_ANGLE_LEAN_BACK = 40

# Forward lean (degrees)
LEAN_FORWARD_ENGAGED = 15
LEAN_FORWARD_MAX = 25

# Position variance (for fidgeting detection)
POSITION_VARIANCE_THRESHOLD = 0.05
FIDGET_DETECTION_FRAMES = 30  # 1 second window

# ======================== GESTURE THRESHOLDS ========================
# Face touching
FACE_TOUCH_DISTANCE_THRESHOLD = 0.10  # normalized distance

# Hand movement (fidgeting)
HAND_VELOCITY_THRESHOLD = 0.02
HAND_FIDGET_FREQUENCY = 5  # movements per second

# Excessive gestures
HAND_GESTURE_AMPLITUDE_THRESHOLD = 0.3

# ======================== CALIBRATION SETTINGS ========================
CALIBRATION_DURATION = 0  # seconds (DISABLED - DeepFace is pre-trained, no calibration needed)
CALIBRATION_FRAMES = CALIBRATION_DURATION * TARGET_FPS

# ======================== ALERT SETTINGS ========================
ALERT_COOLDOWN = 10  # seconds between same alerts
ALERT_DURATION = 2  # seconds to show alert

# Poor posture duration before alert  
POOR_POSTURE_ALERT_FRAMES = 300  # 10 seconds
NOT_FOCUSING_ALERT_FRAMES = 90  # 3 seconds (reduced from 6 - more responsive)
FIDGETING_ALERT_FRAMES = 150  # 5 seconds

# ======================== SENSITIVITY MODES ========================
SENSITIVITY_MODES = {
    'relaxed': {
        'posture_multiplier': 1.3,
        'expression_multiplier': 1.2,
        'gesture_multiplier': 1.5
    },
    'normal': {
        'posture_multiplier': 1.0,
        'expression_multiplier': 1.0,
        'gesture_multiplier': 1.0
    },
    'strict': {
        'posture_multiplier': 0.8,
        'expression_multiplier': 0.85,
        'gesture_multiplier': 0.7
    }
}

DEFAULT_SENSITIVITY = 'normal'

# ======================== VISUALIZATION SETTINGS ========================
# Colors (BGR format)
COLOR_GOOD = (127, 255, 0)      # Green
COLOR_NEUTRAL = (0, 255, 255)   # Yellow
COLOR_BAD = (50, 50, 255)       # Red
COLOR_BLUE = (255, 127, 0)      # Blue
COLOR_WHITE = (255, 255, 255)   # White
COLOR_BLACK = (0, 0, 0)         # Black

# Skeleton mode
SKELETON_MIN_POINTS = 20
SKELETON_MAX_POINTS = 543  # 468 face + 33 pose + 42 hands
SKELETON_DEFAULT_DENSITY = 50  # percentage

# Font
FONT = 'cv2.FONT_HERSHEY_SIMPLEX'
FONT_SCALE_LARGE = 1.0
FONT_SCALE_MEDIUM = 0.7
FONT_SCALE_SMALL = 0.5
FONT_THICKNESS = 2

# ======================== DATA LOGGING ========================
LOG_EVERY_N_FRAMES = 5  # Log every 5 frames to reduce data size
BUFFER_SIZE = 36000  # 30 minutes at 30fps / 5 = 10800, but keep buffer larger
EXPORT_FORMAT = 'csv'  # 'csv', 'json', or 'both'

# ======================== LANDMARK INDICES ========================
# Face landmarks (MediaPipe Face Mesh - 468 points)
FACE_LANDMARKS = {
    'left_eye': [33, 160, 158, 133, 153, 144],
    'right_eye': [362, 385, 387, 263, 373, 380],
    'left_eyebrow': [70, 63, 105, 66, 107],
    'right_eyebrow': [300, 293, 334, 296, 336],
    'mouth_outer': [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409],
    'mouth_inner': [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324],
    'jaw': [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454],
    'nose': [1, 4, 5, 195, 197],
    'face_oval': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
}

# Pose landmarks (MediaPipe Pose - 33 points)
POSE_LANDMARKS = {
    'nose': 0,
    'left_eye_inner': 1,
    'left_eye': 2,
    'left_eye_outer': 3,
    'right_eye_inner': 4,
    'right_eye': 5,
    'right_eye_outer': 6,
    'left_ear': 7,
    'right_ear': 8,
    'mouth_left': 9,
    'mouth_right': 10,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_hip': 23,
    'right_hip': 24,
}

# Hand landmarks (MediaPipe Hands - 21 points per hand)
HAND_LANDMARKS = {
    'wrist': 0,
    'thumb_tip': 4,
    'index_tip': 8,
    'middle_tip': 12,
    'ring_tip': 16,
    'pinky_tip': 20
}
