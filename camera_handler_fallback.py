import cv2
import os
import platform
import logging

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self):
        """Start camera with Docker/host fallback logic."""
        self.logger.info(f"Initializing camera on {platform.system()}")
        
        # Try different access methods
        if os.getenv('DOCKER_ENV') == 'true':
            self.logger.info("Running in Docker environment")
            # Method 1: Try network camera stream
            if self._try_network_stream():
                return True
        else:
            # Direct host access methods
            if platform.system() == 'Windows':
                os.environ['OPENCV_VIDEOIO_PRIORITY_DSHOW'] = '1'
                if self._try_direct_camera(cv2.CAP_DSHOW):
                    return True
            if self._try_direct_camera(cv2.CAP_ANY):
                return True
                
        self.logger.error("All camera access methods failed")
        return False

    def _try_direct_camera(self, backend):
        """Try direct camera access with specified backend."""
        self.logger.info(f"Trying direct camera access with backend {backend}")
        for i in range(3):  # Try first 3 camera indices
            try:
                self.cap = cv2.VideoCapture(i, backend)
                if self.cap.isOpened() and self._verify_frame():
                    self.logger.info(f"Camera {i} opened successfully")
                    return True
                if self.cap:
                    self.cap.release()
            except Exception as e:
                self.logger.warning(f"Camera {i} error: {str(e)}")
        return False

    def _try_network_stream(self):
        """Try accessing camera through network stream."""
        self.logger.info("Attempting network camera stream")
        try:
            # Use host.docker.internal to access host camera
            stream_url = "http://host.docker.internal:8080/video"
            self.cap = cv2.VideoCapture(stream_url)
            if self.cap.isOpened() and self._verify_frame():
                self.logger.info("Network stream working")
                return True
            if self.cap:
                self.cap.release()
        except Exception as e:
            self.logger.warning(f"Network stream error: {str(e)}")
        return False

    def _verify_frame(self):
        """Verify camera can actually capture frames."""
        ret, _ = self.cap.read()
        if not ret:
            self.logger.warning("Couldn't read frame from camera")
            return False
        return True

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
