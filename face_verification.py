import streamlit as st
from live_stream import CameraHandler
from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
import cv2
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FaceVerificationProcessor:
    def __init__(self, db, camera_handler):
        self.db = db
        self.camera_handler = camera_handler
        self.face_handler = FaceRecognitionHandler(db)
        self.face_handler.load_employee_faces()
        self.verified_ids = set()

    def process_frame(self, frame):
        results = self.face_handler.verify_face(frame)
        for emp_id, verified in results.items():
            if verified and emp_id not in self.verified_ids:
                self.verified_ids.add(emp_id)
                emp = self.db.get_employee_by_id(emp_id)
                if emp:  # Only proceed if employee exists
                    status = "Late" if datetime.now().hour >= 9 else "Present"
                    self.db.record_attendance(emp_id, status)
                    cv2.putText(frame, f"Verified: {emp['fullname']}", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    st.session_state.last_verified = emp
        return frame

import uuid

def show_face_verification():
    st.header("Face Verification")
    db = EmployeeDatabase.get_instance()
    camera_handler = CameraHandler()
    processor = FaceVerificationProcessor(db, camera_handler)
    
    # Set a unique_id in session_state if not present
    if 'unique_id' not in st.session_state:
        st.session_state['unique_id'] = str(uuid.uuid4())
    
    st.info("Initializing camera...")
    
    # Use a unique key for the webrtc streamer to avoid duplicate key error
    unique_key = f"face-verification-{st.session_state['unique_id']}"
    
    # Initialize camera only once and store webrtc_ctx in session_state
    if 'webrtc_ctx' not in st.session_state:
        st.session_state['webrtc_ctx'] = camera_handler.initialize_camera(key=unique_key)
    
    webrtc_ctx = st.session_state['webrtc_ctx']
    
    logger.info("webtrc_ctx.video reciver:")
    logger.info(webrtc_ctx.video_receiver)
    logger.info("webtrc_ctx:")
    logger.info(webrtc_ctx)
    
    if webrtc_ctx and webrtc_ctx.video_receiver:
        logger.info("if 1")
        frame = camera_handler.get_frame()
        logger.info("Frame received successfully." if frame is not None else "No frame received.")

        if frame is not None:
            try:
                frame_array = frame.to_ndarray(format="bgr24")
                processed_frame = processor.process_frame(frame_array)
                st.image(processed_frame, channels="BGR")
            except Exception as e:
                st.error(f"Error processing frame: {str(e)}")
    else:
        st.warning("Waiting for camera access permission or camera not initialized.")
    
    if 'last_verified' in st.session_state:
        emp = st.session_state.last_verified
        st.write(f"**Verified Employee:** {emp['fullname']} (ID: {emp['militaryID']})")
        # Updated to use image_binary
        st.image(emp['image_binary'], width=100, caption="Employee Photo")

show_face_verification()
