import streamlit as st
from login_view import check_auth

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

def show_delete_attendance_records():
    """UI for deleting attendance records"""
    st.header("Delete Attendance Records")
    db = EmployeeDatabase()
    
    option = st.radio(
        "Delete by:",
        ["Employee", "Date"]
    )
    
    if option == "Employee":
        employees = db.get_all_employees()
        if not employees:
            st.warning("No employees found!")
            return
            
        employee_names = []
        for emp in employees:
            # Safely handle missing fields
            rank = emp.get('rank', 'N/A')
            fullname = emp.get('fullname', 'Unknown')
            militaryID = emp.get('militaryID', '0000')
            employee_names.append(f"{rank} {fullname} (ID: {militaryID})")
        selected_employee = st.selectbox("Select Employee", employee_names)
        militaryID = employees[employee_names.index(selected_employee)]['militaryID']
        
        if st.button("Delete All Attendance Records"):
            count = db.delete_employee_attendance(militaryID)
            st.success(f"Deleted {count} attendance records for {selected_employee}")
            
    else:  # Delete by Date
        selected_date = st.date_input("Select Date")
        
        if st.button("Delete All Attendance Records"):
            count = db.delete_daily_attendance(selected_date)
            st.success(f"Deleted {count} attendance records for {selected_date.strftime('%Y-%m-%d')}")

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👨‍💼",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Navigation")

# Signout button
if st.sidebar.button("Sign Out"):
    st.session_state.authenticated = False
    st.experimental_rerun()
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