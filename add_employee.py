import streamlit as st
from io import BytesIO
from PIL import Image
from employee_db import EmployeeDatabase
import numpy as np
from deepface import DeepFace

def add_employee_view():
    st.header("Add New Employee")
    db = EmployeeDatabase()

    with st.form("add_employee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            rank = st.text_input("Rank*", placeholder="e.g., Captain")
            fullname = st.text_input("Full Name*", placeholder="e.g., John Doe")
            militaryID = st.text_input("Military ID*", placeholder="Enter unique ID")
            department = st.text_input("Department*", placeholder="e.g., Operations")

        with col2:
            uploaded_file = st.file_uploader("Employee Photo*", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                try:
                    image_data = BytesIO(uploaded_file.read())
                    img = Image.open(image_data)
                    st.image(img, width=150, caption="Uploaded Photo")
                    image_data.seek(0)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

        submitted = st.form_submit_button("Add Employee")

        if submitted:
            if not all([rank, fullname, militaryID, department]) or uploaded_file is None:
                st.error("All fields are required!")
            else:
                try:
                    militaryID = int(militaryID)
                    result = db.add_employee(
                        rank=rank,
                        fullname=fullname,
                        militaryID=militaryID,
                        department=department,
                        image_data=image_data.getvalue()
                    )
                    
                    if "Successfully" in result:
                        st.success(result)
                        st.balloons()
                    else:
                        st.warning(result)
                except ValueError:
                    st.error("Military ID must be a numeric value")
                except Exception as e:
                    st.error(f"Error adding employee: {str(e)}")

def show():
    add_employee_view()

if __name__ == "__main__":
    show()
