import cv2
import logging
import os

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self, max_attempts=3):
        """Start the camera feed with multiple fallback attempts."""
        for i in range(max_attempts):
            try:
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    self.logger.info(f"Successfully opened camera at index {i}")
                    return True
                self.cap.release()
            except Exception as e:
                self.logger.warning(f"Camera attempt {i} failed: {str(e)}")
        
        # Try environment variable as fallback
        try:
            cam_source = int(os.getenv('CAMERA_SOURCE', '0'))
            self.cap = cv2.VideoCapture(cam_source)
            if self.cap.isOpened():
                self.logger.info(f"Using camera from ENV variable: {cam_source}")
                return True
        except Exception as e:
            self.logger.error(f"All camera attempts failed: {str(e)}")
        
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