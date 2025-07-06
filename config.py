"""
Configuration file for static values and constants used across the project.
"""

# DroneKit connection settings
# if physical vehicle
#DRONEKIT_CONNECTION_STRING = "dev/tty0" 
# if simulator
DRONEKIT_CONNECTION_STRING = "tcp:127.0.0.1:5762"

DRONEKIT_WAIT_READY = False
DRONEKIT_BAUD = 57600

# Gesture recognition settings
GESTURE_SWITCH_DISTANCE = 200  # Distance in cm to switch between hand and body gestures

# Gesture types
GESTURE_TYPES = {
    1: 'hand',
    2: 'body',
}

# Gesture mappings
GESTURES = {
    1: 'up',
    2: 'down',
    3: 'right',
    4: 'left',
    5: 'further',
    6: 'closer',
    7: 'land',
    8: 'take_off',
    9: 'photo',
    10: 'video',
    11: 'video_pause',
    12: 'emergency',
    13: 'follow',
    14: 'palm',
    15: 'no_class',
}

# Model/data paths for detectors.py
BODY_MODEL_PATH = 'model/body_detection/body_detection_model.tflite'
HAND_MODEL_PATH = 'model/hand_detection/hand_detection_model.tflite'
BODY_LABELS_PATH = 'model/body_detection/body_gesture_labels.csv'
HAND_LABELS_PATH = 'model/hand_detection/hand_gesture_labels.csv'

# Default values for drone movement and actions
DEFAULT_MOVE_DISTANCE = 1 # meters
DEFAULT_TAKEOFF_ALTITUDE = 2 # meters
DEFAULT_SPEED = 1 # meters/second

# Known values for distance estimation
KNOWN_FACE_WIDTH = 17.2  # centimeter
FOCAL_LENGTH = 453.49  # calculated from reference image 

# Detection thresholds
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.5 # Minimum confidence for detection
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.5 # Minimum confidence for tracking
GESTURE_ACCURACY_THRESHOLD = 0.75 # Minimum accuracy for gesture recognition



# Default video capture device
VIDEO_CAPTURE_DEVICE = 0

# Default video settings
VIDEO_CODEC = 'XVID'
VIDEO_FPS = 25.0
VIDEO_SIZE = (640, 480)

# Video and photo output directory
OUTPUT_DIR = 'drone_media'

# GUI colors
COLOR_PRIMARY = "#8d2ac9"
COLOR_TEXT = "white"
COLOR_ARMED = "green"
COLOR_DISARMED = "red"
COLOR_UNKNOWN = "grey"

# GUI frame size
GUI_FRAME_WIDTH = 900  # Width of the GUI frame
GUI_FRAME_HEIGHT = 720  # Height of the GUI frame



