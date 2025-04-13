import streamlit as st
from live_stream import CameraHandler
from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
import cv2
from datetime import datetime

class FaceVerificationProcessor:
    def __init__(self, db, camera_handler):
        """
        Initialize the face verification processor with a database and camera handler.
        """
        self.db = db
        self.camera_handler = camera_handler
        self.face_handler = FaceRecognitionHandler(db)
        self.face_handler.load_employee_faces()  # Load embeddings
        self.verified_ids = set()

    def process_frame(self, frame):
        """
        Process each video frame to verify faces.
        """
        results = self.face_handler.verify_face(frame)
        
        for emp_id, verified in results.items():
            if verified and emp_id not in self.verified_ids:
                self.verified_ids.add(emp_id)
                emp = self.db.get_employee_by_id(emp_id)
                current_time = datetime.now()
                status = "Late" if current_time.hour >= 9 else "Present"
                self.db.record_attendance(emp_id, status)
                
                # Annotate the frame with verification details
                cv2.putText(frame, f"Verified: {emp['fullname']}", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Update the session state with the last verified employee
                st.session_state.last_verified = emp

        return frame


def show_face_verification():
    """
    Main face verification interface using CameraHandler and FaceVerificationProcessor.
    """
    st.header("Face Verification")

    # Initialize database and camera handler
    db = EmployeeDatabase()
    camera_handler = CameraHandler()

    # Initialize face verification processor
    processor = FaceVerificationProcessor(db, camera_handler)

    # Initialize the camera feed
    st.info("Initializing camera...")
    webrtc_ctx = camera_handler.initialize_camera(key="face-verification")

    # Process video frames in real-time
    if webrtc_ctx and webrtc_ctx.video_transformer:
        frame = camera_handler.get_frame()
        if frame is not None:
            processed_frame = processor.process_frame(frame.to_ndarray(format="bgr24"))

    # Display verification results
    if 'last_verified' in st.session_state:
        emp = st.session_state.last_verified
        with st.container():
            st.write(f"**Verified Employee:** {emp['fullname']} (ID: {emp['militaryID']})")
            st.write(f"Rank: {emp['rank']}, Department: {emp['department']}")
            if emp.get('image_data'):
                st.image(emp['image_data'], width=100)
            else:
                st.warning("No image available")

            if st.button("OK"):
                del st.session_state.last_verified
                st.experimental_rerun()

# Call the function to display the face verification interface
show_face_verification()