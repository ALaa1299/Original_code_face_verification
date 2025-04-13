import streamlit as st
from login_view import check_auth

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👨‍💼",
    layout="wide"
)

# Check authentication before showing any content
check_auth()

from add_employee import show as show_add_employee
from view_employees import show as show_view_employees
from record_attendance import show as show_record_attendance
from update_employee import show as show_update_employee
from delete_employee import show as show_delete_employee
from export_attendance import show as show_export_attendance
from face_verification import show_face_verification
from user_view import show as show_user_management
from employee_db import EmployeeDatabase
from datetime import datetime
from delete_attendance import show as show_delete_attendance_records

# Sidebar navigation
st.sidebar.title("Navigation")

# Signout button
if st.sidebar.button("Sign Out"):
    st.session_state.authenticated = False
    st.rerun()

# Navigation options
nav_options = [
    "Add Employee",
    "View Employees", 
    "Record Attendance",
    "Update Employee",
    "Delete Employee",
    "Export Attendance",
    "Face Verification",
    "Delete Attendance Records"
]

# Add User Management for admins
if st.session_state.get('role') == 'admin':
    nav_options.append("User Management")
    
page = st.sidebar.radio("Go to", nav_options)

# Main content area
st.title("Employee Management System")

# Page routing
if page == "Add Employee":
    show_add_employee()
elif page == "View Employees":
    show_view_employees()
elif page == "Record Attendance":
    show_record_attendance()
elif page == "Update Employee":
    show_update_employee()
elif page == "Delete Employee":
    show_delete_employee()
elif page == "Export Attendance":
    show_export_attendance()
elif page == "Face Verification":
    show_face_verification()
elif page == "Delete Attendance Records":
    show_delete_attendance_records()
elif page == "User Management":
    show_user_management()