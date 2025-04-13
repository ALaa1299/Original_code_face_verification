from employee_db import EmployeeDatabase
import streamlit as st
import os
from io import BytesIO

def show():
    st.header("Add New Employee")
    db = EmployeeDatabase()
    
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            rank = st.text_input("Rank*", placeholder="e.g. Captain")
            fullname = st.text_input("Full Name*", placeholder="e.g. John Doe")
            militaryID = st.text_input("Military ID*", placeholder="Enter unique ID")
            department = st.text_input("Department*", placeholder="e.g. Operations")
            
        with col2:
            uploaded_file = st.file_uploader("Employee Photo*", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                # Read image data into memory
                image_data = BytesIO(uploaded_file.read())
                # Display the uploaded image
                st.image(image_data, width=150)
                # Reset pointer for database storage
                image_data.seek(0)
        
        submitted = st.form_submit_button("Add Employee")
        if submitted:
            if not all([rank, fullname, militaryID, department]) or uploaded_file is None:
                st.error("All fields are required!")
            else:
                try:
                    militaryID = int(militaryID)
                    # Store image binary data directly in MongoDB
                    result = db.add_employee(
                        rank, 
                        fullname, 
                        militaryID, 
                        department, 
                        image_data.getvalue()  # Store binary data
                    )
                    if "Successfully" in result:
                        st.success(result)
                    elif "already exists" in result:
                        st.warning(result)
                    else:
                        st.error(result)
                except ValueError:
                    st.error("Military ID must be a number")
                except Exception as e:
                    st.error(f"Error saving employee: {str(e)}")
