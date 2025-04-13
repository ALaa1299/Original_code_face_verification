import streamlit as st
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer
from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
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

    def transform(self, frame):
        frame = frame.to_ndarray(format="bgr24")
        
        # Process frame for face recognition
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
                        
                        # Draw verification info on frame
                        cv2.putText(frame, f"Verified: {emp['fullname']}", (20, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        except Exception as e:
            st.error(f"Face recognition error: {str(e)}")
            
        return frame

def main():
    st.title("Live Face Verification Stream")
    
    ctx = webrtc_streamer(
        key="face-verification",
        video_transformer_factory=FaceRecognitionTransformer,
        async_transform=True
    )
    
    if ctx.video_transformer:
        st.write("Verification results will appear on the video stream")

if __name__ == "__main__":
    main()
