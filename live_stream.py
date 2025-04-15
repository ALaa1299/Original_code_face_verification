import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import logging

logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self):
        """
        Initialize the camera handler. This manages the camera feed via WebRTC.
        """
        self.webrtc_ctx = None  # Placeholder for WebRTC context

    def initialize_camera(self, key="camera-feed", frame_callback=None):
        """
        Prompt the user for permission and initialize the WebRTC streamer for camera feed.
        Accepts a frame_callback function to process frames asynchronously.
        """
        st.info("Please grant permission for camera access in your browser.")
        logger.info("Initializing camera with key: %s", key)

        def callback(frame: av.VideoFrame):
            logger.info("Received a new video frame for processing.")
            if frame_callback:
                processed_frame = frame_callback(frame)
                logger.info("Processed frame returned from callback.")
                return processed_frame
            logger.info("No frame_callback provided, returning original frame.")
            return frame

        # Initialize the WebRTC streamer
        self.webrtc_ctx = webrtc_streamer(
            key=key,
            mode=WebRtcMode.SENDRECV,  # Send and receive video
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 320},  # Lower resolution width
                    "height": {"ideal": 240},  # Lower resolution height
                    "frameRate": {"ideal": 15}  # Lower frame rate
                },
                "audio": False
            },  # Video-only with constraints
            async_processing=True,  # Enable async processing for smooth performance
            video_frame_callback=callback
        )

        if self.webrtc_ctx.video_receiver:
            logger.info("Camera initialized successfully, video_receiver is available.")
            st.success("Camera initialized successfully! Start using the app.")
        else:
            logger.warning("Waiting for camera access permission, video_receiver not yet available.")
            st.warning("Waiting for camera access permission...")

        return self.webrtc_ctx
