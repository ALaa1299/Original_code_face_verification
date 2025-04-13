import cv2
import platform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_camera_access():
    """Test different camera access methods."""
    logger.info(f"Testing camera access on {platform.system()}")
    
    # Method 1: DirectShow in Docker
    logger.info("Trying Docker camera access...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                logger.info("Docker access successful!")
                return True
            cap.release()
    except Exception as e:
        logger.warning(f"Docker access failed: {str(e)}")
    
    # Method 2: Direct host access
    logger.info("Trying direct host access...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                logger.info("Host access successful!")
                return True
            cap.release()
    except Exception as e:
        logger.warning(f"Host access failed: {str(e)}")
    
    logger.error("All access methods failed")
    return False

if __name__ == "__main__":
    test_camera_access()
