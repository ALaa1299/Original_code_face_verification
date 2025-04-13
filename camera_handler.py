import cv2
import logging
import os

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.logger = logging.getLogger(__name__)

    def start_camera(self, max_attempts=3):
        """Start the camera feed with multiple fallback strategies."""
        # First check if we should use simulation mode
        if os.getenv('CAMERA_SIMULATION', 'false').lower() == 'true':
            self.simulation_mode = True
            self.logger.warning("Running in camera simulation mode")
            return True

        # Try different backends and sources
        backends = [cv2.CAP_ANY, cv2.CAP_V4L2, cv2.CAP_DSHOW, cv2.CAP_FFMPEG]
        sources = [0, '/dev/video0', '/dev/video1', '/dev/video2', os.getenv('CAMERA_SOURCE', '0')]

        for backend in backends:
            for source in sources:
                try:
                    self.cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source, backend)
                    if self.cap.isOpened():
                        self.logger.info(f"Opened camera: {source} with backend {backend}")
                        self.simulation_mode = False
                        return True
                    self.cap.release()
                except Exception as e:
                    self.logger.warning(f"Camera open failed: {source} {backend}: {str(e)}")

        # Fallback to simulation mode if all attempts fail
        self.simulation_mode = True
        self.logger.error("All camera attempts failed. Running in simulation mode.")
        self.logger.error("To fix camera access:")
        self.logger.error("1. For containers: add '--device /dev/video0' to docker run")
        self.logger.error("2. Check camera permissions: 'ls -l /dev/video*'")
        self.logger.error("3. Set CAMERA_SOURCE env var or CAMERA_SIMULATION=true")
        return True

    def get_frame(self):
        """Get frame from camera or simulated frame."""
        if hasattr(self, 'simulation_mode') and self.simulation_mode:
            # Generate a simple gradient test pattern
            import numpy as np
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "CAMERA SIMULATION MODE", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            return frame
            
        if self.cap and self.cap.isOpened():
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