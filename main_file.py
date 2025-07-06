import threading
from utils.image_processing import ImageProcessingController
from utils.gui import GUI


def main():
    """Main entry point for the gesture-controlled drone application.
    This script initializes the image processing controller and starts the GUI application."""

    # Create the controller object that holds all state and logic
    controller = ImageProcessingController()

    # create threads for image processing and control loop
    im_pro = threading.Thread(target=controller.image_processing)
    control_loop = threading.Thread(target=controller.control_loop)

    # Start the threads
    im_pro.start()
    control_loop.start()

    # Start the GUI application
    app = GUI(controller)
    app.run(app.update_video, app.update_status)


if __name__ == "__main__":
    main()