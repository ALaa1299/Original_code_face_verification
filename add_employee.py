import streamlit as st
from io import BytesIO
from PIL import Image
from employee_db import EmployeeDatabase

def add_employee_view():
    st.header("Add New Employee")
    db = EmployeeDatabase()  # Initialize the database

    # Create a form for user input
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            rank = st.text_input("Rank*", placeholder="e.g., Captain")
            fullname = st.text_input("Full Name*", placeholder="e.g., John Doe")
            militaryID = st.text_input("Military ID*", placeholder="Enter unique ID")
            department = st.text_input("Department*", placeholder="e.g., Operations")

        with col2:
            uploaded_file = st.file_uploader("Employee Photo*", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                # Read image data and display preview
                image_data = BytesIO(uploaded_file.read())
                st.image(image_data, width=150, caption="Uploaded Photo")
                image_data.seek(0)  # Reset pointer for processing

        submitted = st.form_submit_button("Add Employee")

        if submitted:
            # Validate inputs
            if not all([rank, fullname, militaryID, department]) or uploaded_file is None:
                st.error("All fields are required!")
            else:
                try:
                    # Ensure military ID is numeric
                    militaryID = int(militaryID)

                    # Prepare binary image data
                    img = Image.open(image_data)
                    img_byte_arr = BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_binary = img_byte_arr.getvalue()

                    # Add employee to the database
                    result = db.add_employee(rank, fullname, militaryID, department, img_binary)
                    
                    # Handle database response
                    if "Successfully" in result:
                        st.success(result)
                        st.experimental_rerun()  # Refresh view
                    elif "already exists" in result:
                        st.warning(result)
                    else:
                        st.error(result)
                except ValueError:
                    st.error("Military ID must be a numeric value.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")