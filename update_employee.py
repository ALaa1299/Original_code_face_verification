from employee_db import EmployeeDatabase
import streamlit as st

def show():
    st.header("Update Employee")
    db = EmployeeDatabase()
    
    with st.form("update_form"):
        militaryID = st.text_input("Military ID to Update")
        rank = st.text_input("New Rank", placeholder="Leave blank to keep current")
        fullname = st.text_input("New Full Name", placeholder="Leave blank to keep current")
        department = st.text_input("New Department", placeholder="Leave blank to keep current")
        uploaded_file = st.file_uploader("New Employee Photo", type=['jpg', 'jpeg', 'png'], accept_multiple_files=False)
        
        submitted = st.form_submit_button("Update Employee")
        if submitted:
            update_data = {}
            if rank: update_data['rank'] = rank
            if fullname: update_data['fullname'] = fullname
            if department: update_data['department'] = department
            if uploaded_file is not None:
                try:
                    # Convert militaryID to int for database query
                    militaryID_int = int(militaryID)
                    
                    # Get current employee data
                    current_employee = db.collection.find_one({"militaryID": militaryID_int})
                    
                    # Read new image as binary data
                    image_data = uploaded_file.read()
                    update_data['image_data'] = image_data
                except Exception as e:
                    st.error(f"Error handling image update: {str(e)}")
            
            if not update_data:
                st.error("No fields to update!")
            else:
                try:
                    militaryID = int(militaryID)
                    result = db.update_employee(militaryID, update_data)
                    if "Successfully" in result:
                        st.success(result)
                    elif "No employee" in result:
                        st.warning(result)
                    else:
                        st.error(result)
                except ValueError:
                    st.error("Military ID must be a number")