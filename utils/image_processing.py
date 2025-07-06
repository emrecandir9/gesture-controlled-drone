import os
import time
import datetime
import logging
import cv2
import config
from utils.cvfpscalc import CvFpsCalc
from utils.drone_movement import Drone_Movement
from utils.detectors import Detectors
import config

gesture_types = config.GESTURE_TYPES
gestures = config.GESTURES

drone_movement = Drone_Movement()
detector = Detectors(config.DEFAULT_MIN_DETECTION_CONFIDENCE, config.DEFAULT_MIN_TRACKING_CONFIDENCE)

class ImageProcessingController:
    """Controller for image processing and gesture detection.
    It manages the state of the drone, processes video frames, and handles gesture recognition.
    It also provides methods to control the drone based on detected gestures."""

    def __init__(self):
        self.detector = detector
        self.move_functions = drone_movement
        self.gesture_types = gesture_types
        self.gestures = gestures

        # All state variables here
        self.gesture_type = 0
        self.hand_gesture_id = 0
        self.body_gesture_id = 0
        self.distance = 0
        self.frame = None
        self.video_record = False
        self.take_photo = False
        self.stop_video_record = False
        self.last_hand_gesture_id = None
        self.hand_gesture_count = 0
        self.last_body_gesture_id = None
        self.body_gesture_count = 0
        self.gui_frame = None

    def image_processing(self):
        """Main loop for image processing and gesture detection."""

        cap = cv2.VideoCapture(config.VIDEO_CAPTURE_DEVICE)
        indicator_pos = (30, 30)
        photo_indicator_timer = 0
        wait_for_pose = 5
        

        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR)

        time_now = datetime.datetime.now()
        video_path = os.path.join(config.OUTPUT_DIR, f"video_{time_now.strftime('%d-%m-%y-%I-%M-%S')}.avi")
        fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
        out = cv2.VideoWriter(video_path, fourcc, config.VIDEO_FPS, config.VIDEO_SIZE)

        cvFpsCalc = CvFpsCalc(buffer_len=10)
        while cap.isOpened():
            ret, frame = cap.read()
            record = frame.copy() if frame is not None else None
            if not ret or frame is None:
                logging.warning('Ignoring empty camera frame.')
                break
            
            
            fps = cvFpsCalc.get()
            cv2.putText(frame, f"FPS: {fps}", (int(cap.get(4)/2), 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255, 255, 255), 4, cv2.LINE_AA)

            if self.video_record:
                cv2.circle(frame, indicator_pos, 12, (0, 0, 255), -1)

            if photo_indicator_timer > 0:
                cv2.circle(frame, indicator_pos, 12, (0, 255, 0), -1)
                photo_indicator_timer -= 1
                wait_for_pose -= 1

            detected_distance = self.detector.detect_face(frame)
            if detected_distance is not None:
                self.distance = detected_distance

            if self.distance < config.GESTURE_SWITCH_DISTANCE:
                self.gesture_type = 1
                gesture_id = self.detector.detect_hand_gesture(frame)
                if gesture_id is not None:
                    if gesture_id == self.last_hand_gesture_id:
                        self.hand_gesture_count += 1
                    else:
                        self.hand_gesture_count = 1
                        self.last_hand_gesture_id = gesture_id
                    if self.hand_gesture_count >= int(fps):
                        self.hand_gesture_id = gesture_id
                        self.hand_gesture_count = 0
                else:
                    self.hand_gesture_count = 0
                    self.last_hand_gesture_id = None
            elif self.distance >= config.GESTURE_SWITCH_DISTANCE:
                self.gesture_type = 2
                gesture_id = self.detector.detect_body_gesture(frame)
                if gesture_id is not None:
                    if gesture_id == self.last_body_gesture_id:
                        self.body_gesture_count += 1
                    else:
                        self.body_gesture_count = 1
                        self.last_body_gesture_id = gesture_id
                    if self.body_gesture_count >= int(fps):
                        self.body_gesture_id = gesture_id
                        self.body_gesture_count = 0
                else:
                    self.body_gesture_count = 0
                    self.last_body_gesture_id = None

            self.gui_frame = frame

            if self.video_record and record is not None:
                out.write(record)

            if self.take_photo and record is not None:
                wait_for_pose = int(fps) if fps > 0 else 15
                photo_indicator_timer = int(fps) if fps > 0 else 15
                self.take_photo = False

            if wait_for_pose < 5 and record is not None:
                time_now = datetime.datetime.now()
                photo_path = os.path.join(config.OUTPUT_DIR, f"photo_{time_now.strftime('%d-%m-%y-%I-%M-%S')}.jpg")
                cv2.imwrite(photo_path, record)
                wait_for_pose = 10

            if self.stop_video_record:
                out.release()
                self.video_record = False
                self.stop_video_record = False
                time_now = datetime.datetime.now()
                video_path = os.path.join(config.OUTPUT_DIR, f"video_{time_now.strftime('%d-%m-%y-%I-%M-%S')}.avi")
                out = cv2.VideoWriter(video_path, fourcc, config.VIDEO_FPS, config.VIDEO_SIZE)

    def control_loop(self):
        """Control loop for managing drone actions based on detected gestures."""

        while True:
            time.sleep(0.2)
            if self.gesture_type == 1 and self.hand_gesture_id is not None and self.hand_gesture_id > 0:
                self.move_functions.move(self.hand_gesture_id)
                if self.hand_gesture_id == 9:
                    time.sleep(2)
                    self.take_photo = True
                elif self.hand_gesture_id == 10:
                    self.video_record = True
                elif self.hand_gesture_id == 11:
                    self.stop_video_record = True
                self.hand_gesture_id = 0

            elif self.gesture_type == 2 and self.body_gesture_id is not None and self.body_gesture_id > 0:
                self.move_functions.move(self.body_gesture_id)
                if self.body_gesture_id == 9:
                    time.sleep(2)
                    self.take_photo = True
                elif self.body_gesture_id == 10:
                    self.video_record = True
                elif self.body_gesture_id == 11:
                    self.stop_video_record = True
                self.body_gesture_id = 0

    def get_gui_frame(self):
        return self.gui_frame
    
    def get_distance(self):
        return self.distance
    
    def get_gesture_type(self):
        return self.gesture_type    
    
    def get_hand_gesture_id(self):
        return self.hand_gesture_id
    
    def get_body_gesture_id(self):
        return self.body_gesture_id
    
    def get_altitude(self):
        try:
            return self.move_functions.uav.location.global_relative_frame.alt
        except AttributeError:
            return 0
        
    def get_speed(self):
        try:
            return self.move_functions.uav.airspeed
        except AttributeError:
            return 0
        
    def get_arm_status(self):
        try:
            return self.move_functions.uav.armed
        except AttributeError:
            return False
    