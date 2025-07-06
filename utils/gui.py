import argparse
import customtkinter
from tkinter import *
import config
import cv2
import datetime
import imutils
from PIL import Image, ImageTk

from utils.image_processing import ImageProcessingController

class GUI(customtkinter.CTk):
    """
    Main GUI class for the gesture-controlled drone project.
    Provides real-time video display and status indicators.
    """
    def __init__(self, image_pro, *args, **kwargs):
        """
        Initializes the GUI with a title, size, and key bindings.
        """

        super().__init__(*args, **kwargs)
        self.gesture_types = config.GESTURE_TYPES
        self.gestures = config.GESTURES  
        self.controller = image_pro

        self.flight_begin = None
        self.time_taken = False
        self.gui_armstatus = 0
        self.gui_curges = '-'

        self.title("Gesture Controlled Drone GUI")
        self.geometry("1200x700")
        self.bind('<Escape>', lambda e: self.quit())
        self.label_widget = Label(self, bd=3, bg='#8d2ac9')
        self.label_widget.pack(ipadx=0, ipady=0, expand=True)
        # Status labels (static)
        self.label_alt = customtkinter.CTkLabel(master=self, text="ALTITUDE (m)", width=170, height=30, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_alt.place(relx=0.5, rely=0.5, x=400, y=-200)
        self.label_speed = customtkinter.CTkLabel(master=self, text="SPEED (m/s)", width=170, height=31, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_speed.place(relx=0.5, rely=0.5, x=400, y=-50)
        self.label_time = customtkinter.CTkLabel(master=self, text="FLIGHT TIME", width=170, height=31, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_time.place(relx=0.5, rely=0.5, x=400, y=100)
        self.label_distodrone = customtkinter.CTkLabel(master=self, text="DIS. TO DRONE (cm)", width=170, height=31, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_distodrone.place(relx=0.5, rely=0.5, x=-570, y=-200)
        self.label_gestype = customtkinter.CTkLabel(master=self, text="GESTURE TYPE", width=170, height=31, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_gestype.place(relx=0.5, rely=0.5, x=-570, y=-50)
        self.label_curges = customtkinter.CTkLabel(master=self, text="CURRENT GESTURE", width=170, height=31, fg_color="#8d2ac9", text_color='white', corner_radius=8, anchor='n', pady=10, font=('', 16))
        self.label_curges.place(relx=0.5, rely=0.5, x=-570, y=100)
        self.label_title = customtkinter.CTkLabel(master=self, text="GESTURE CONTROLLED DRONE", width=600, height=40, text_color='#8d2ac9', corner_radius=8, pady=10, font=('', 38))
        self.label_title.place(relx=0.5, rely=0.5, x=-315, y=-360)
        
        # Value labels (dynamic)
        self.label_alt_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 30))
        self.label_alt_value.place(relx=0.5, rely=0.5, x=400, y=-167)
        self.label_speed_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 30))
        self.label_speed_value.place(relx=0.5, rely=0.5, x=400, y=-17)
        self.label_time_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 30))
        self.label_time_value.place(relx=0.5, rely=0.5, x=400, y=133)
        self.label_distodrone_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 30))
        self.label_distodrone_value.place(relx=0.5, rely=0.5, x=-570, y=-167)
        self.label_gestype_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 22))
        self.label_gestype_value.place(relx=0.5, rely=0.5, x=-570, y=-17)
        self.label_curges_value = customtkinter.CTkLabel(master=self, text="", fg_color="#8d2ac9", text_color='white', width=170, height=70, corner_radius=8, anchor="center", font=('', 20))
        self.label_curges_value.place(relx=0.5, rely=0.5, x=-570, y=133)
        self.label_arm = customtkinter.CTkLabel(master=self, text="", fg_color='grey', text_color='white', width=200, height=30, corner_radius=8, anchor="center", font=('', 25))
        self.label_arm.place(relx=0.5, rely=0.5, x=-100, y=290)

    def run(self, frame_func, status_func):
        """Starts the GUI and sets up periodic updates for status and frame functions."""

        self.after(10000, status_func)
        self.after(10000, frame_func)
        self.mainloop()

    def status(self, altitude, speed, flight_time, dis_to_drone, ges_type, cur_ges, arm_status):
        """Updates the status labels with current values."""

        self.label_alt_value.configure(text=str(altitude))
        self.label_speed_value.configure(text=str(speed))
        self.label_time_value.configure(text=str(flight_time))
        self.label_distodrone_value.configure(text=str(dis_to_drone))
        self.label_gestype_value.configure(text=str(ges_type))
        self.label_curges_value.configure(text=str(cur_ges))
        if arm_status == 1:
            self.label_arm.configure(text='ARMED', fg_color='green')
        elif arm_status == 2:
            self.label_arm.configure(text='DISARMED', fg_color='red')
        else:
            self.label_arm.configure(text='UNKNOWN', fg_color='grey')

    def update_video(self):
        """Updates the video frame in the GUI."""

        gui_frame = self.controller.get_gui_frame()
        if gui_frame is not None:
            rgb_frame = cv2.cvtColor(gui_frame, cv2.COLOR_BGR2RGB)
            rgb_frame = imutils.resize(rgb_frame, width=config.GUI_FRAME_WIDTH)
            captured_image = Image.fromarray(rgb_frame)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
        self.label_widget.after(33, self.update_video)

    def update_status(self):
        """Updates the status labels with current information."""

        gui_alt = round(self.controller.get_altitude(),1) if hasattr(self.controller, "get_altitude") else 0
        gui_speed = round(self.controller.get_speed(), 1) if hasattr(self.controller, "get_speed") else 0
        armed = self.controller.get_arm_status() if hasattr(self.controller, "get_arm_status") else 0
        
        if armed and not self.time_taken:
            self.gui_armstatus = 1
            self.flight_begin = datetime.datetime.now()
            self.time_taken = True
        elif not armed:
            self.gui_armstatus = 2

        current_time = datetime.datetime.now()
        gui_fltime = '00:00'
        if armed and self.flight_begin:
            flight_time = current_time - self.flight_begin
            gui_fltime = str(flight_time)[2:7]

        gui_dis = round(self.controller.get_distance(), 1) if hasattr(self.controller, "get_distance") else 0
        gui_gestype = self.gesture_types[self.controller.get_gesture_type()].upper() if self.controller.get_gesture_type() else '-'

        
        if self.controller.get_gesture_type() == 1:
            self.gui_curges = self.gestures[self.controller.get_hand_gesture_id()].upper() if self.controller.get_hand_gesture_id() else '-'
        elif self.controller.get_gesture_type() == 2:
            self.gui_curges = self.gestures[self.controller.get_body_gesture_id()].upper() if self.controller.get_body_gesture_id() else '-'

        self.status(gui_alt, gui_speed, gui_fltime, gui_dis, gui_gestype, self.gui_curges, self.gui_armstatus)
        self.after(500, self.update_status)

