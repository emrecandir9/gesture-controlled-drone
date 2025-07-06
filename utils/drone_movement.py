import time
import logging
from utils.dronekit_func import Dronekit_Func
from dronekit import LocationGlobalRelative
import config

class Drone_Movement:
    """Class for controlling drone movements using DroneKit.
    It provides methods to move the drone in various directions, take off, land, and perform other actions based on gestures."""

    def __init__(self):
        """Initializes the Drone_Movement class with a Dronekit_Func instance."""
        self.dronekit_functions = Dronekit_Func(
            config.DRONEKIT_CONNECTION_STRING,
            wait_ready=config.DRONEKIT_WAIT_READY,
            baud=config.DRONEKIT_BAUD
        )
        self.uav = self.dronekit_functions.vehicle

    def move(self, gesture_id):
        """Dispatches the gesture to the corresponding drone movement method using config.GESTURES."""
        gesture_name = config.GESTURES.get(gesture_id)
        if not gesture_name or gesture_name == "no_class":
            logging.info(f"No movement for gesture_id: {gesture_id} ({gesture_name})")
            return None
        method = getattr(self, gesture_name, None)
        if callable(method):
            return method()
        logging.warning(f"No method found for gesture: {gesture_name}")
        return None

    def up(self):
        """Moves the drone up by a default distance defined in config."""

        logging.info("Move up triggered.")
        if not self.uav.armed:
            logging.warning("Cannot ascend: vehicle not armed.")
            return False
        meters_up = config.DEFAULT_MOVE_DISTANCE
        k = self.uav.location.global_relative_frame
        desired_alt = k.alt + meters_up
        cmd = LocationGlobalRelative(k.lat, k.lon, desired_alt)
        self.uav.simple_goto(cmd)
        time.sleep(0.1)
        while self.uav.location.global_relative_frame.alt < desired_alt - 0.2:
            logging.info("Ascending...")
            time.sleep(0.5)
        logging.info("Reached desired altitude.")
        return True

    def down(self):
        """Moves the drone down by a default distance defined in config."""

        logging.info("Move down triggered.")
        if not self.uav.armed:
            logging.warning("Cannot descend: vehicle not armed.")
            return False
        meters_down = config.DEFAULT_MOVE_DISTANCE
        k = self.uav.location.global_relative_frame
        if k.alt <= 1.1:
            logging.warning("Altitude too low to descend further.")
            return False
        desired_alt = max(0, k.alt - meters_down)
        cmd = LocationGlobalRelative(k.lat, k.lon, desired_alt)
        self.uav.simple_goto(cmd)
        while self.uav.location.global_relative_frame.alt > desired_alt + 0.2:
            logging.info("Descending...")
            time.sleep(0.5)
        logging.info("Reached desired altitude.")
        return True

    def right(self):
        """Moves the drone to the right by a default distance defined in config.""" 

        logging.info("Move right triggered.")
        if not self.uav.armed:
            logging.warning("Cannot move right: vehicle not armed.")
            return False
        speed = config.DEFAULT_SPEED
        self.uav.airspeed = speed
        distance = config.DEFAULT_MOVE_DISTANCE
        des_time = int(distance / speed)
        self.dronekit_functions.send_ned_velocity(0, -speed, 0, des_time)
        time.sleep(des_time+0.5)  
        logging.info("Move right complete.")
        return True

    def left(self):
        """Moves the drone to the left by a default distance defined in config."""
        
        logging.info("Move left triggered.")
        if not self.uav.armed:
            logging.warning("Cannot move left: vehicle not armed.")
            return False
        speed = config.DEFAULT_SPEED
        self.uav.airspeed = speed
        distance = config.DEFAULT_MOVE_DISTANCE
        des_time = int(distance / speed)
        self.dronekit_functions.send_ned_velocity(0, speed, 0, des_time)
        time.sleep(des_time+0.5)  
        logging.info("Move left complete.")
        return True

    def further(self):
        """Moves the drone further away by a default distance defined in config."""

        logging.info("Move further triggered.")
        if not self.uav.armed:
            logging.warning("Cannot move further: vehicle not armed.")
            return False
        speed = config.DEFAULT_SPEED
        self.uav.airspeed = speed
        distance = config.DEFAULT_MOVE_DISTANCE
        des_time = int(distance / speed)
        self.dronekit_functions.send_ned_velocity(-speed, 0, 0, des_time)
        time.sleep(des_time+0.5) 
        logging.info("Move further complete.")
        return True

    def closer(self):
        """Moves the drone closer by a default distance defined in config."""
        
        
        logging.info("Move closer triggered.")
        if not self.uav.armed:
            logging.warning("Cannot move closer: vehicle not armed.")
            return False
        speed = config.DEFAULT_SPEED
        self.uav.airspeed = speed
        distance = config.DEFAULT_MOVE_DISTANCE
        des_time = int(distance / speed)
        self.dronekit_functions.send_ned_velocity(speed, 0, 0, des_time)
        time.sleep(des_time+0.5)  
        logging.info("Move closer complete.")
        return True

    def land(self):
        """Initiates the landing sequence for the drone."""
        
        logging.info("Landing initiated.")
        if not self.uav.armed:
            logging.warning("Cannot land: vehicle not armed.")
            return False
        self.uav.mode = "LAND"

        logging.info("Vehicle mode set to LAND.")
        while self.uav.location.global_relative_frame.alt > 0.5:
            logging.info(f"Current altitude: {self.uav.location.global_relative_frame.alt}")
            time.sleep(1)
            if not self.uav.armed:
                break
        logging.info("Landing completed.")
        return True

    def take_off(self):
        """Initiates the takeoff sequence for the drone."""
        
        logging.info("Takeoff initiated.")
        take_off_alt = config.DEFAULT_TAKEOFF_ALTITUDE
        self.dronekit_functions.arm_and_takeoff(take_off_alt)
        while True:
            current_alt = self.uav.location.global_relative_frame.alt
            if current_alt >= take_off_alt * 0.8:
                break
            time.sleep(1)
        return True

    def photo(self):
        """Initiates the photo capture sequence and takes a photo."""   

        logging.info("Photo capture initiated.")
        if not self.uav.armed:
            logging.warning("Cannot capture photo: vehicle not armed.")
            return False
        logging.info("Photo captured.")
        return True

    def video(self):
        """Initiates the video recording sequence and starts recording."""
        
        logging.info("Video recording initiated.")
        if not self.uav.armed:
            logging.warning("Cannot start video: vehicle not armed.")
            return False
        logging.info("Video recording started.")
        return True

    def video_pause(self):
        """Pauses the video recording sequence"""
        
        logging.info("Video recording pause triggered.")
        if not self.uav.armed:
            logging.warning("Cannot pause video: vehicle not armed.")
            return False
        logging.info("Video recording paused.")
        return True

    def emergency(self):
        """Initiates the emergency procedure for the drone."""

        if not self.uav.armed:
            logging.warning("Cannot perform emergency landing: vehicle not armed.")
            return False
        logging.error("Emergency mode initiated!")

        # Different emergency actions can be added here
        # setting a LAND mode or failsafe mode
        # i set the mode to LAND
        self.land()
        return True

    def follow(self):
        """Initiates the follow mode for the drone."""
        
        if not self.uav.armed:
            logging.warning("Cannot initiate follow mode: vehicle not armed.")
            return False
        logging.info("Follow mode initiated.")

        # TODO: Implement follow mode logic here
        # follow mode will be desgigned to follow a person or object

        return True

    def palm(self):
        """Initiates the palm mode for the drone."""
        
        if not self.uav.armed:
            logging.warning("Cannot initiate palm mode: vehicle not armed.")
            return False
        logging.info("Palm mode initiated.")

        # TODO: Implement palm mode logic here
        # palm mode only available for hand gesture, and will be desgigned to move the drone in 3D space based on palm position

        return True







