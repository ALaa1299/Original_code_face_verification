import cv2
import logging
import os
import platform

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self):
        """Start camera with Windows-specific optimizations."""
        self.logger.info("Initializing camera on Windows")
        self.logger.info(f"OpenCV version: {cv2.__version__}")
        
        # Windows-specific setup
        if platform.system() == 'Windows':
            os.environ['OPENCV_VIDEOIO_PRIORITY_DSHOW'] = '1'
            backend = cv2.CAP_DSHOW
        else:
            backend = cv2.CAP_ANY

        # First detect available cameras
        available_cams = []
        for i in range(3):  # Check first 3 indices
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                available_cams.append(i)
                cap.release()
        
        if not available_cams:
            self.logger.error("No cameras detected")
            return False

        self.logger.info(f"Available cameras: {available_cams}")
        
        # Try each available camera
        for cam_index in available_cams:
            try:
                self.cap = cv2.VideoCapture(cam_index, backend)
                if self.cap.isOpened():
                    ret, _ = self.cap.read()
                    if ret:
                        self.logger.info(f"Successfully opened camera index {cam_index}")
                        return True
                    self.cap.release()
            except Exception as e:
                self.logger.error(f"Error with camera {cam_index}: {str(e)}")
                if self.cap:
                    self.cap.release()

        self.logger.error("All backends failed")
        return False

    def get_frame(self):
        """Get frame from camera."""
        if not self.cap or not self.cap.isOpened():
            return None
            
        try:
            ret, frame = self.cap.read()
            return frame if ret else None
        except Exception as e:
            self.logger.error(f"Frame error: {str(e)}")
            return None

    def release_camera(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
