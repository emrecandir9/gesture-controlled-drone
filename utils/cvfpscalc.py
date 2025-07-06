from collections import deque
import cv2 as cv


class CvFpsCalc:
    """
    Utility class for calculating frames per second (FPS) in real-time video processing.
    """

    def __init__(self, buffer_len=1):
        """Initializes the FPS calculator with a specified buffer length."""

        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        """
        Calculate the average FPS based on the time difference between frames.
        """
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)
        if not self._difftimes:
            return 0.0
        avg_time = sum(self._difftimes) / len(self._difftimes)
        if avg_time == 0:
            return 0.0
        fps = 1000.0 / avg_time

        return round(fps, 2)
