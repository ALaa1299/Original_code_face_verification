import cv2
import logging

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self):
        """Start the camera feed with robust Windows/Docker support."""
        import platform
        import os
        
        self.logger.info("Starting camera initialization")
        self.logger.info(f"System: {platform.system()}")
        self.logger.info(f"Python: {platform.python_version()}")
        self.logger.info(f"OpenCV: {cv2.__version__}")
        
        # Try different backends in order of preference
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_V4L2, "Video4Linux"),
            (cv2.CAP_ANY, "Default")
        ]
        
        for backend, name in backends:
            try:
                self.logger.info(f"Trying {name} backend")
                self.cap = cv2.VideoCapture(0, backend)
                if self.cap.isOpened():
                    ret, _ = self.cap.read()
                    if ret:
                        self.logger.info(f"Success with {name} backend")
                        return True
                    self.cap.release()
        
        self.logger.error("All camera backends failed to initialize")
        return False
            
        except Exception as e:
            self.logger.error(f"Camera initialization error: {str(e)}")
            if self.cap:
                self.cap.release()
            return False

    def get_frame(self):
        """Capture a frame from the camera with error handling."""
        if self.cap is not None and self.cap.isOpened():
            try:
                self.logger.debug("Attempting to capture frame from camera")
                ret, frame = self.cap.read()
                if ret:
                    self.logger.debug("Successfully captured frame")
                    return frame
                self.logger.warning("Failed to read frame from camera")
                self.logger.debug(f"Camera properties: Width={self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}, Height={self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            except Exception as e:
                self.logger.error(f"Frame capture error: {str(e)}")
                self.logger.debug(f"Camera status: IsOpened={self.cap.isOpened()}")
        else:
            self.logger.warning("Attempted to get frame from null or closed camera")
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
