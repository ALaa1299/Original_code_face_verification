import streamlit as st
from employee_db import EmployeeDatabase

def show():
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
            
        military_id_input = st.text_input("Enter Military ID to search:")
        
        if military_id_input:
            filtered_employees = [emp for emp in employees if str(emp.get('militaryID', '')) == military_id_input]
            if not filtered_employees:
                st.warning("No employees found with that Military ID!")
                return
            
            employee_names = []
            for emp in filtered_employees:
                # Safely handle missing fields
                rank = emp.get('rank', 'N/A')
                fullname = emp.get('fullname', 'Unknown')
                militaryID = emp.get('militaryID', '0000')
                employee_names.append(f"{rank} {fullname} (ID: {militaryID})")
            selected_employee = employee_names[0]  # Select the first match
            militaryID = filtered_employees[0]['militaryID']
        
        if st.button("Delete All Attendance Records"):
            count = db.delete_employee_attendance(militaryID)
            st.success(f"Deleted {count} attendance records for {selected_employee}")
            
    else:  # Delete by Date
        selected_date = st.date_input("Select Date")
        
        if st.button("Delete All Attendance Records"):
            count = db.delete_daily_attendance(selected_date)
            st.success(f"Deleted {count} attendance records for {selected_date.strftime('%Y-%m-%d')}")
