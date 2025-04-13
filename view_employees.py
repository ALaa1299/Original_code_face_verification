import streamlit as st
import cv2
import os
from io import BytesIO
from PIL import Image
from employee_db import EmployeeDatabase

def show():
    """Display all employees with filtering and attendance deletion options"""
    st.header("View Employees")
    db = EmployeeDatabase()
    
    # Filter options
    st.sidebar.header("Filter Options")
    rank_filter = st.sidebar.text_input("Filter by Rank")
    id_filter = st.sidebar.text_input("Filter by Military ID")
    name_filter = st.sidebar.text_input("Filter by Name")
    dept_filter = st.sidebar.text_input("Filter by Department")
    
    # Get and filter employees
    employees = db.get_all_employees()
    filtered_employees = [
        emp for emp in employees
        if (not rank_filter or rank_filter.lower() in emp.get('rank', '').lower())
        and (not id_filter or id_filter in str(emp.get('militaryID', '')))
        and (not name_filter or name_filter.lower() in emp.get('fullname', '').lower())
        and (not dept_filter or dept_filter.lower() in emp.get('department', '').lower())
    ]
    
    if not filtered_employees:
        st.warning("No matching employees found!")
        return
        
    # Display filtered employees with images and delete buttons
    for emp in filtered_employees:
            cols = st.columns([1, 3, 1])  # Image, Info, Delete button
            
            with cols[0]:  # Image column
                if emp.get('image_binary'):
                    try:
                        img = Image.open(BytesIO(emp['image_binary']))
                        st.image(img, width=100)
                    except Exception as e:
                        st.error(f"Error loading image: {str(e)}")
                else:
                    st.warning("No image available")
            
            with cols[1]:  # Info column
                st.write(f"{emp.get('rank', 'N/A')} : {emp.get('fullname', 'Unknown')}")
                st.write(f"Military ID: {emp.get('militaryID', '0000')}")
                st.write(f"Department: {emp.get('department', 'N/A')}")
                
                # Show attendance records in collapsible section
                attendance = db.get_attendance_by_employee(emp['militaryID'])
                if attendance:
                    with st.expander(f"View Attendance Records ({len(attendance)})"):
                        for record in attendance:
                            st.write(f"- {record['status']} at {record['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                st.write("---")
            
            with cols[2]:  # Delete button column
                if st.button("Delete Attendance", key=f"del_att_{emp['militaryID']}"):
                    count = db.delete_employee_attendance(emp['militaryID'])
                    st.success(f"Deleted {count} attendance records")
                    st.rerun()
