import cv2
import logging
import os

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self, max_attempts=3):
        """Start the camera feed with multiple fallback strategies."""
        # Try different backends
        backends = [
            cv2.CAP_ANY,        # Auto-detect backend
            cv2.CAP_V4L2,       # V4L2 backend
            cv2.CAP_DSHOW,      # DirectShow
            cv2.CAP_FFMPEG      # FFMPEG
        ]

        # Try different sources
        sources = [
            0,                  # Default camera index
            '/dev/video0',      # Common Linux device path
            '/dev/video1',
            '/dev/video2',
            '/dev/video*',      # Wildcard pattern
            os.getenv('CAMERA_SOURCE', '0')  # From environment
        ]

        for backend in backends:
            for source in sources:
                try:
                    if isinstance(source, int) or source.isdigit():
                        self.cap = cv2.VideoCapture(int(source), backend)
                    else:
                        self.cap = cv2.VideoCapture(source, backend)
                    
                    if self.cap.isOpened():
                        self.logger.info(f"Opened camera: {source} with backend {backend}")
                        return True
                    self.cap.release()
                except Exception as e:
                    self.logger.warning(f"Failed to open {source} with backend {backend}: {str(e)}")

        self.logger.error("All camera attempts failed. Possible solutions:")
        self.logger.error("1. Check camera is connected and recognized by OS")
        self.logger.error("2. Verify container has camera access permissions")
        self.logger.error("3. Try setting CAMERA_SOURCE environment variable")
        
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