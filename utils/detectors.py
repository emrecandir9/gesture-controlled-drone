import os
import csv
import cv2
import mediapipe as mp
import tensorflow as tf
import numpy as np
import logging
import config
from utils.helper_func import HelperFunc
from utils.distance_estimation import DistanceEstimator

# Set TensorFlow logging level
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

# Model/data paths from config
BODY_MODEL_PATH = config.BODY_MODEL_PATH
HAND_MODEL_PATH = config.HAND_MODEL_PATH

def load_labels(label_path):
    """Load gesture labels from a CSV file."""
    try:
        with open(label_path, encoding='utf-8-sig') as f:
            return [row[0] for row in csv.reader(f)]
    except Exception as e:
        logging.error(f"Failed to load labels from {label_path}: {e}")
        return []

BODY_GESTURE_LABELS = load_labels(config.BODY_LABELS_PATH)
HAND_GESTURE_LABELS = load_labels(config.HAND_LABELS_PATH)

functions = HelperFunc()

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_detection = mp.solutions.face_detection



class Detectors:
    """
    Class for detecting body and hand gestures using MediaPipe and TensorFlow Lite models.
    It provides methods to classify gestures, detect body and hand gestures, and estimate face distance.
    """

    def __init__(self, min_detection_confidence, min_tracking_confidence):
        """ Initializes the Detectors with specified confidence thresholds for detection and tracking."""
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.pose = mp_pose.Pose(
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.face_detector = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=self.min_detection_confidence
        )

    def classify_gesture(self, model_path, landmark_list):
        """Run gesture classification using a TFLite model and return (class_id, accuracy)."""
        try:
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            interpreter.set_tensor(input_details[0]['index'], np.array([landmark_list], dtype=np.float32))
            interpreter.invoke()
            result = interpreter.get_tensor(output_details[0]['index'])
            result = np.squeeze(result)
            class_id = int(np.argmax(result))
            accuracy = float(round(result[class_id], 2))
            return class_id, accuracy
        except Exception as e:
            logging.error(f"Gesture classification failed: {e}")
            return -1, 0.0

    def detect_body_gesture(self, frame):
        """
        Detects body gesture from the given frame, draws bounding box and label if confident.
        Returns the gesture class index or None if not detected/confident.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        if results.pose_landmarks:
            landmark_list = functions.calc_landmark_list(rgb_frame, results.pose_landmarks, use_pose=True)
            preprocessed = functions.pre_process_landmark(landmark_list)
            class_id, accuracy = self.classify_gesture(BODY_MODEL_PATH, preprocessed)
            if accuracy > config.GESTURE_ACCURACY_THRESHOLD and 0 <= class_id < len(BODY_GESTURE_LABELS):
                brect = functions.calc_bounding_rect(rgb_frame, results.pose_landmarks)
                frame = functions.rect_corners(frame, brect)
                frame.flags.writeable = True
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2),
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=2)
                )
                label = BODY_GESTURE_LABELS[class_id-1] if 0 <= class_id-1 < len(BODY_GESTURE_LABELS) else "Unknown"
                info_text = f"{label} {accuracy:.2f}"
                frame = functions.text_with_background(frame, info_text, (brect[0], brect[1]))
                return class_id
        return None

    def detect_hand_gesture(self, frame):
        """
        Detects right hand gesture from the given frame, draws bounding box and label if confident.
        Returns the gesture class index or None if not detected/confident.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Use the handedness info for each hand
                hand_label = results.multi_handedness[idx].classification[0].label if hasattr(results, 'multi_handedness') else None
                if hand_label == 'Left': # in flipped image, right hand is considered left hand in MediaPipe
                    landmark_list = functions.calc_landmark_list(rgb_frame, hand_landmarks, use_pose=False)
                    preprocessed = functions.pre_process_landmark(landmark_list)
                    class_id, accuracy = self.classify_gesture(HAND_MODEL_PATH, preprocessed)
                    if accuracy > config.GESTURE_ACCURACY_THRESHOLD and 0 <= class_id < len(HAND_GESTURE_LABELS):
                        brect = functions.calc_bounding_rect(rgb_frame, hand_landmarks)
                        frame = functions.rect_corners(frame, brect)
                        frame.flags.writeable = True
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=3),
                            mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2)
                        )
                        label = HAND_GESTURE_LABELS[class_id-1] if 0 <= class_id-1 < len(HAND_GESTURE_LABELS) else "Unknown"
                        info_text = f"{label} {accuracy:.2f}"
                        frame = functions.text_with_background(frame, info_text, (brect[0], brect[1]))
                        return class_id
        return None

    def detect_face(self, frame):
        """Detects faces in the given frame and estimates distance to the face if detected.
        Returns the estimated distance in centimeters or None if no face is detected."""

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(rgb_frame)
        frame_height, frame_width = frame.shape[:2]
        if results.detections:
            for face in results.detections:
                bbox = face.location_data.relative_bounding_box
                face_rect = np.multiply(
                    [bbox.xmin, bbox.ymin, bbox.width, bbox.height],
                    [frame_width, frame_height, frame_width, frame_height]
                ).astype(int)
                accuracy = round(face.score[0], 2) if face.score else 0.0
                functions.rect_corners(frame, face_rect, (121, 44, 250), th=3)
                try:
                    distance = DistanceEstimator().distance_estimator(
                        frame, face_rect, config.KNOWN_FACE_WIDTH, cv2.FONT_HERSHEY_PLAIN
                    )
                except Exception as e:
                    logging.error(f"Face distance estimation failed: {e}")
                    distance = None
                return distance
        return None


