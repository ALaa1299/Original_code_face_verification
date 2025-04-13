import cv2
import logging

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self):
        """Start the camera feed with error handling."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.logger.error("Failed to open camera at index 0")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Camera initialization error: {str(e)}")
            return False

    def get_frame(self):
        """Capture a frame from the camera with error handling."""
        if self.cap is not None and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    return frame
                self.logger.warning("Failed to read frame from camera")
            except Exception as e:
                self.logger.error(f"Frame capture error: {str(e)}")
        return None

    def release_camera(self):
        """Release the camera resources safely."""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                self.logger.error(f"Camera release error: {str(e)}")
            finally:
                self.cap = None