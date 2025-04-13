from employee_db import EmployeeDatabase
import streamlit as st

def show():
    st.header("Record Attendance")
    db = EmployeeDatabase()
    
    with st.form("attendance_form"):
        militaryID = st.text_input("Military ID")
        status = st.selectbox("Status", ["present", "absent", "late", "on leave"])
        
        submitted = st.form_submit_button("Record Attendance")
        if submitted:
            try:
                militaryID = int(militaryID)
                result = db.record_attendance(militaryID, status)
                st.success(result)
            except ValueError:
                st.error("Military ID must be a number")