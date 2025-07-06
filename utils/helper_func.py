import numpy as np
import cv2
import itertools
import copy
import csv
import os

class HelperFunc():
    """Helper functions for landmark and image processing."""
    def __init__(self):
        pass

    def calc_bounding_rect(self, image, landmarks):
        """Calculate the bounding rectangle for the given landmarks in the image."""

        image_width, image_height = image.shape[1], image.shape[0]
        landmark_array = np.empty((0, 2), int)
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point = [np.array((landmark_x, landmark_y))]
            landmark_array = np.append(landmark_array, landmark_point, axis=0)
        x, y, w, h = cv2.boundingRect(landmark_array)
        return [x, y, w, h]

    def calc_landmark_list(self, image, landmarks, use_pose):
        """Calculate the landmark points from the landmarks in the image."""

        image_width, image_height = image.shape[1], image.shape[0]
        landmark_point = []
        if not use_pose:
            for _, landmark in enumerate(landmarks.landmark):
                landmark_x = min(int(landmark.x * image_width), image_width - 1)
                landmark_y = min(int(landmark.y * image_height), image_height - 1)
                landmark_point.append([landmark_x, landmark_y])
        else:
            pose_list = [11, 12, 13, 14, 15, 16]  # arms landmark points
            for num, landmark in enumerate(landmarks.landmark):
                if num in pose_list:
                    landmark_x = min(int(landmark.x * image_width), image_width - 1)
                    landmark_y = min(int(landmark.y * image_height), image_height - 1)
                    landmark_point.append([landmark_x, landmark_y])
        return landmark_point

    def pre_process_landmark(self, landmark_list):
        """Pre-process the landmark list by normalizing and centering it."""

        temp_landmark_list = copy.deepcopy(landmark_list)
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]
            temp_landmark_list[index][0] -= base_x
            temp_landmark_list[index][1] -= base_y
        temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
        max_value = max(list(map(abs, temp_landmark_list)))
        if max_value == 0:
            return temp_landmark_list
        temp_landmark_list = [n / max_value for n in temp_landmark_list]
        return temp_landmark_list

    def rect_corners(self, image, rect_points, color=(121,22,76), DIV=6, th=2, opacity=0.3, draw_overlay=False):
        """Draw corners on the rectangle defined by rect_points."""
        
        x, y, w, h = rect_points
        top_right_corner = np.array(
            [[x + w // DIV, y], [x, y], [x, y + h // DIV]], dtype=np.int32
        )
        cv2.rectangle(image, (x, y), (x + w, y + h), color, th // 2)
        cv2.polylines(image, [top_right_corner], False, color, th)
        top_left_corner = np.array(
            [[(x + w) - w // DIV, y], [x + w, y], [x + w, y + h // DIV]], dtype=np.int32
        )
        cv2.polylines(image, [top_left_corner], False, color, th)
        bottom_right_corner = np.array(
            [[x + w // DIV, y + h], [x, y + h], [x, (y + h) - h // DIV]], dtype=np.int32
        )
        cv2.polylines(image, [bottom_right_corner], False, color, th)
        bottom_left_corner = np.array(
            [[x + w, (y + h) - h // DIV], [x + w, y + h], [(x + w) - w // DIV, y + h]], dtype=np.int32,
        )
        if draw_overlay:
            overlay = image.copy()
            cv2.rectangle(overlay, rect_points, color, -1)
            new_img = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
            image = new_img
        cv2.polylines(image, [bottom_left_corner], False, color, th)
        return image

    def text_with_background(self, image, text, position, fonts=cv2.FONT_HERSHEY_PLAIN,
        scaling=1, color=(121,44,250), th=1, draw_corners=True, up=0):

        """Draw text with a background rectangle on the image."""

        x, y = position
        y = y - up
        info_text = text
        (w, h), p = cv2.getTextSize(info_text, fonts, scaling, th)
        cv2.rectangle(image, (x - p, y + p), (x + w + p, y - h - p), (0, 0, 0), -1)
        if draw_corners:
            rect_points = [x - p, y - h - p, w + p + p, h + p + p]
            self.rect_corners(image, rect_points, color, th=th, DIV=4)
        if text != "":
            cv2.putText(image, info_text, (x, y), fonts, scaling, color, th, cv2.LINE_AA)
        return image

# Helper functions for notebooks

    def is_normalized(self,list):
        """Checks if a list of numbers is normalized."""
        if not list:
            return False

        s = sum(list)
        if s == 0:
            return False

        for x in list:
            if x < -1 or x > 1:
                return False

        return True

    def write_csv(self, number, landmark_list, use_pose):
        """Write the landmark list to a CSV file."""

        if not use_pose:
            csv_path = 'model/hand_detection/keypoint.csv'
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                if self.is_normalized(landmark_list):
                    writer.writerow([number, *landmark_list])

        else: 
            csv_path = 'model/body_detection/body_keypoints.csv'
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                if self.is_normalized(landmark_list):
                    writer.writerow([number, *landmark_list])       
        return

    def get_key_from_value(self,dictionary, target_value):
        """Get the key from a dictionary based on the target value."""
        for key, value in dictionary.items():
            if value == target_value:
                return key
