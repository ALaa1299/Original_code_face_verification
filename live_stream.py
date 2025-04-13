import streamlit as st
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer, WebRtcMode
from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
from camera_handler import CameraHandler
import cv2
import numpy as np
from datetime import datetime
import tempfile

class FaceRecognitionTransformer(VideoTransformerBase):
    def __init__(self):
        self.db = EmployeeDatabase()
        self.face_handler = FaceRecognitionHandler(self.db)
        self.face_handler.load_employee_faces()
        self.verified_ids = set()
        self.camera_handler = CameraHandler()
        self.use_fallback = False

    def transform(self, frame):
        if not self.use_fallback:
            try:
                frame = frame.to_ndarray(format="bgr24")
                return self._process_frame(frame)
            except Exception as e:
                st.warning(f"WebRTC stream failed, falling back to OpenCV: {str(e)}")
                self.use_fallback = True
                self.camera_handler.start_camera()
        
        if self.use_fallback:
            fallback_frame = self.camera_handler.get_frame()
            if fallback_frame is not None:
                return self._process_frame(fallback_frame)
            return np.zeros((480, 640, 3), dtype=np.uint8)

    def _process_frame(self, frame):
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
                cv2.imwrite(tmp.name, frame)
                results = self.face_handler.verify_face(frame)
                
                for emp_id, verified in results.items():
                    if verified and emp_id not in self.verified_ids:
                        self.verified_ids.add(emp_id)
                        emp = self.db.get_employee_by_id(emp_id)
                        current_time = datetime.now()
                        status = "Late" if current_time.hour >= 9 else "Present"
                        self.db.record_attendance(emp_id, status)
                        
                        cv2.putText(frame, f"Verified: {emp['fullname']}", (20, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        except Exception as e:
            st.error(f"Face recognition error: {str(e)}")
        return frame

def main():
    st.title("Face Verification System")
    
    if st.checkbox("Use WebRTC Streaming (recommended)", value=True):
        ctx = webrtc_streamer(
            key="face-verification",
            video_transformer_factory=FaceRecognitionTransformer,
            mode=WebRtcMode.SENDRECV,
            async_transform=True,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={
                "video": True,
                "audio": False
            }
        )
        
        if ctx.video_transformer:
            st.write("Verification results will appear on the video stream")
    else:
        st.warning("Using OpenCV camera fallback")
        transformer = FaceRecognitionTransformer()
        transformer.use_fallback = True
        if not transformer.camera_handler.start_camera():
            st.error("Failed to initialize camera. Please check camera connection.")
            return
            
        FRAME_WINDOW = st.empty()
        stop_button = st.button("Stop Verification")
        
        while not stop_button:
            frame = transformer.transform(None)  # None forces use of fallback
            if frame is not None:
                FRAME_WINDOW.image(frame, channels="BGR")
            if stop_button:
                break

if __name__ == "__main__":
    main()
