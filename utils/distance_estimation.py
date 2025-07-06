import config
from utils.helper_func import HelperFunc
import logging


functions = HelperFunc()

class DistanceEstimator:
    """
    Estimates the distance to a face in a frame using known face width and camera focal length.
    """
    def calc_dist(self, focal_length, known_face_width_cm, face_height_in_frame_px):
        """Calculate the distance to the face based on the focal length, known face width, and height of the face in the frame."""

        if face_height_in_frame_px <= 0:
            logging.warning("Face height in frame is zero or negative; cannot estimate distance.")
            return 0
        return (known_face_width_cm * focal_length) / face_height_in_frame_px

    def distance_estimator(self, frame, face_rect, known_face_width, font):
        """ Estimates the distance to a face in the frame and displays it on the frame."""

        x, y, w, h = face_rect
        focal = config.FOCAL_LENGTH
        distance = self.calc_dist(focal, known_face_width, h)
        functions.text_with_background(
            frame,
            f"Distance: {int(distance)}cm",
            (x, y - 10),
            font,
            color=(121, 44, 250),
        )
        return distance
