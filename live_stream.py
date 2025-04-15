import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import logging
import queue
import av
from typing import Union
from threading import Lock
import asyncio
import sys
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception as e:
        logger.warning(f"Failed to set WindowsSelectorEventLoopPolicy: {e}")

RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]}
    ]
})

class VideoProcessor:
    def __init__(self):
        self.frame_queue = queue.Queue(maxsize=1)

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        try:
            self.frame_queue.put_nowait(frame.to_ndarray(format="bgr24"))
        except queue.Full:
            logger.warning("Frame queue full, dropping frame.")
        return frame

class CameraHandler:
    def __init__(self):
        self.webrtc_ctx = None
        self.video_processor = VideoProcessor()
        self.lock = Lock()

    def initialize_camera(self, key=None):
        st.info("Please grant permission for camera access in your browser.")

        if key is None:
            if "camera_key" not in st.session_state:
                st.session_state.camera_key = f"camera-feed-{uuid.uuid4()}"
            key = st.session_state.camera_key
        else:
            if f"{key}_unique" not in st.session_state:
                st.session_state[f"{key}_unique"] = f"{key}-{uuid.uuid4()}"
            key = st.session_state[f"{key}_unique"]

        try:
            self.webrtc_ctx = webrtc_streamer(
                key=key,
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={
                    "video": {"width": {"ideal": 640}, "height": {"ideal": 480}, "frameRate": {"ideal": 30}},
                    "audio": False,
                },
                video_processor_factory=VideoProcessor,
                async_processing=True,
            )

            if self.webrtc_ctx.video_processor:
                self.video_processor = self.webrtc_ctx.video_processor
                st.success("Camera initialized successfully!")
            else:
                st.warning("Waiting for camera access...")

        except Exception as e:
            st.error(f"Failed to initialize camera: {e}")
            logger.error(f"Camera initialization error: {e}")
            return None

        return self.webrtc_ctx

    def get_frame(self) -> Union[None, av.VideoFrame]:
        if not self.webrtc_ctx or not self.webrtc_ctx.video_processor:
            return None

        try:
            with self.lock:
                if not self.video_processor.frame_queue.empty():
                    return self.video_processor.frame_queue.get_nowait()
            return None
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            return None

    def release(self):
        with self.lock:
            if self.webrtc_ctx:
                try:
                    self.webrtc_ctx.video_receiver.stop()
                    logger.info("Camera resources released")
                except Exception as e:
                    logger.error(f"Error releasing camera: {e}")
                finally:
                    self.webrtc_ctx = None
