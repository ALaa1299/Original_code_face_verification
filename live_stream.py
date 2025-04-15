import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode

class CameraHandler:
    def __init__(self):
        """
        Initialize the camera handler. This manages the camera feed via WebRTC.
        """
        self.webrtc_ctx = None  # Placeholder for WebRTC context

    def initialize_camera(self, key="camera-feed"):
        """
        Prompt the user for permission and initialize the WebRTC streamer for camera feed.
        """
        st.info("Please grant permission for camera access in your browser.")

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
            async_processing=True  # Enable async processing for smooth performance
        )

        if self.webrtc_ctx.video_receiver:
            st.success("Camera initialized successfully! Start using the app.")
        else:
            st.warning("Waiting for camera access permission...")

        return self.webrtc_ctx

    def get_frame(self):
        """
        Retrieve the current frame from the WebRTC streamer.
        """
        if self.webrtc_ctx and self.webrtc_ctx.video_receiver:
            return self.webrtc_ctx.video_receiver.get_frame()
        return None