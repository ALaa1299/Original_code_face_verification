import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from employee_db import EmployeeDatabase
from face_recognition_handler import FaceRecognitionHandler
import cv2
import tempfile
from datetime import datetime

class FaceVerificationTransformer:
    def __init__(self, db):
        self.db = db
        self.face_handler = FaceRecognitionHandler(db)
        self.face_handler.load_employee_faces()
        self.verified_ids = set()

    def process_frame(self, frame):
        frame = frame.to_ndarray(format="bgr24")
        
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
                        
                        # Store verified employee in session state
                        st.session_state.last_verified = emp
                        st.experimental_rerun()
        except Exception as e:
            st.error(f"Face recognition error: {str(e)}")
            
        return frame

def show_face_verification():
    """Face verification interface using WebRTC"""
    st.header("Face Verification")
    db = EmployeeDatabase()
    
    if 'verified_ids' not in st.session_state:
        st.session_state.verified_ids = set()
    
    # Initialize transformer
    transformer = FaceVerificationTransformer(db)
    
    # WebRTC streamer
    ctx = webrtc_streamer(
        key="face-verification",
        video_frame_callback=transformer.process_frame,
        mode=WebRtcMode.SENDRECV,
        async_processing=True
    )
    
    # Display verification results
    if 'last_verified' in st.session_state:
        emp = st.session_state.last_verified
        with st.container():
            st.write(f"**Verified Employee:** {emp['fullname']} (ID: {emp['militaryID']})")
            st.write(f"Rank: {emp['rank']}, Department: {emp['department']}")
            st.image(emp['image_path'], width=100)
            
            if st.button("OK"):
                del st.session_state.last_verified
                st.experimental_rerun()
