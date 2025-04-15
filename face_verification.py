import streamlit as st
from live_stream import CameraHandler
from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
import cv2
from datetime import datetime
import numpy as np
import logging
import av

logger = logging.getLogger(__name__)

class FaceVerificationProcessor:
    def __init__(self, db):
        self.db = db
        self.face_handler = FaceRecognitionHandler(db)
        self.face_handler.load_employee_faces()
        self.verified_ids = set()

    def process_frame(self, frame: av.VideoFrame) -> av.VideoFrame:
        logger.info("Processing a new video frame for face verification.")
        # Convert VideoFrame to ndarray
        img = frame.to_ndarray(format="bgr24")
        results = self.face_handler.verify_face(img)
        for emp_id, verified in results.items():
            if verified and emp_id not in self.verified_ids:
                self.verified_ids.add(emp_id)
                emp = self.db.get_employee_by_id(emp_id)
                if emp:  # Only proceed if employee exists
                    status = "Late" if datetime.now().hour >= 9 else "Present"
                    self.db.record_attendance(emp_id, status)
                    cv2.putText(img, f"Verified: {emp['fullname']}", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    st.session_state.last_verified = emp
                    logger.info(f"Employee verified: {emp['fullname']} (ID: {emp['militaryID']})")
        # Return processed frame as VideoFrame
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def show_face_verification():
    st.header("Face Verification")
    db = EmployeeDatabase.get_instance()
    processor = FaceVerificationProcessor(db)
    camera_handler = CameraHandler()
    st.info("Initializing camera...")

    # Use a unique key for the webrtc streamer to avoid duplicate key error
    unique_key = f"face-verification-{st.session_state.get('unique_id', 'default')}"

    # Initialize camera with frame callback for async processing
    webrtc_ctx = camera_handler.initialize_camera(
        key=unique_key,
        frame_callback=processor.process_frame
    )
    logger.info("Camera initialized and frame callback set.")

    if 'last_verified' in st.session_state:
        emp = st.session_state.last_verified
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**Verified Employee:** {emp['fullname']} (ID: {emp['militaryID']})")
            st.image(emp['image_binary'], width=100, caption="Employee Photo")
        with col2:
            if st.button("OK"):
                del st.session_state['last_verified']

show_face_verification()
