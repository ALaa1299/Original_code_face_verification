import streamlit as st
from employee_db import EmployeeDatabase
from face_recognition_handler import FaceRecognitionHandler
from camera_handler import CameraHandler
import cv2
import tempfile
import os
from datetime import datetime

def show_face_verification():
    """Continuous face verification interface using modular components"""
    st.header("Face Verification")
    db = EmployeeDatabase()
    
    # Initialize handlers
    face_handler = FaceRecognitionHandler(db)
    camera_handler = CameraHandler()
    
    # Initialize session state
    if 'verification_in_progress' not in st.session_state:
        st.session_state.verification_in_progress = False
    if 'verified_ids' not in st.session_state:
        st.session_state.verified_ids = set()
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Verification", disabled=st.session_state.verification_in_progress):
            st.session_state.verification_in_progress = True
            st.session_state.verified_ids = set()
            st.experimental_rerun()
    with col2:
        if st.button("Stop Verification", disabled=not st.session_state.verification_in_progress):
            st.session_state.verification_in_progress = False
            st.experimental_rerun()
    
    # Continuous verification process
    if st.session_state.verification_in_progress:
        st.warning("Continuous face verification in progress...")
        st.write("Camera feed will remain active until stopped")
        
        # Load employee face data
        face_handler.load_employee_faces()
        
        if not face_handler.known_embeddings:
            st.error("No valid employee face data available")
            st.session_state.verification_in_progress = False
            return

        # Start camera with retries and detailed error handling
        if not camera_handler.start_camera():
            st.error("""
            Camera initialization failed. Possible causes:
            1. No camera connected
            2. Camera in use by another application
            3. Permission issues (on Linux/Mac)
            
            Please check your camera connection and try again.
            """)
            st.session_state.verification_in_progress = False
            camera_handler.release_camera()
            return
            
        FRAME_WINDOW = st.empty()
        
        while st.session_state.verification_in_progress:
            frame = camera_handler.get_frame()
            if frame is None:
                st.warning("No camera feed available. Trying to reconnect...")
                if not camera_handler.start_camera():
                    st.error("Camera connection lost. Please check camera and try again.")
                    st.session_state.verification_in_progress = False
                    break
                continue
                
            # Verify faces in frame
            results = face_handler.verify_face(frame)
            
            # Process verification results
            for emp_id, verified in results.items():
                if verified and emp_id not in st.session_state.verified_ids:
                    st.session_state.verified_ids.add(emp_id)
                    employee_data = db.get_all_employees()  # Fetch employee data
                    emp = next(emp for emp in employee_data if emp['militaryID'] == emp_id)
                    current_time = datetime.now()
                    if current_time.hour >= 9:
                        db.record_attendance(emp_id, "Late")
                    else:
                        db.record_attendance(emp_id, "Present")
                    
                    # Display verified employee data
                    with st.container():
                        st.write(f"**Verified Employee:** {emp['fullname']} (ID: {emp['militaryID']})")
                        st.write(f"Rank: {emp['rank']}, Department: {emp['department']}")
                        st.image(emp['image_path'], width=100)
                        
                        if st.button("OK", key=f"ok_{emp['militaryID']}"):
                            st.session_state.verified_ids.remove(emp['militaryID'])
                            st.experimental_rerun()
            
            # Display the frame
            FRAME_WINDOW.image(frame, channels="BGR")
        
        # Release camera
        camera_handler.release_camera()
