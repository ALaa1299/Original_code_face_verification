from streamlit_webrtc import webrtc_streamer, WebRtcMode

class CameraHandler:
    def __init__(self):
        """
        Initialize the camera handler. This manages the camera feed via WebRTC.
        """
        self.webrtc_ctx = None  # Placeholder for WebRTC context

    def initialize_camera(self, key="camera-feed"):
        """
        Initialize the WebRTC streamer for camera feed.
        """
        self.webrtc_ctx = webrtc_streamer(
            key=key,
            mode=WebRtcMode.SENDRECV,  # Send and receive video
            media_stream_constraints={"video": True, "audio": False},  # Video-only
            async_processing=True,  # Enable async processing for smooth performance
        )
        return self.webrtc_ctx

    def get_frame(self):
        """
        Retrieve the current frame from the WebRTC streamer.
        """
        if self.webrtc_ctx and self.webrtc_ctx.video_receiver:
            return self.webrtc_ctx.video_receiver.get_frame()
        return None