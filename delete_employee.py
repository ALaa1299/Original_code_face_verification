from employee_db import EmployeeDatabase
import streamlit as st

def show():
    st.header("Delete Employee")
    db = EmployeeDatabase()
    
    with st.form("delete_form"):
        militaryID = st.text_input("Military ID to Delete")
        
        submitted = st.form_submit_button("Delete Employee")
        if submitted:
            try:
                militaryID = int(militaryID)
                result = db.delete_employee(militaryID)
                if "Successfully" in result:
                    st.success(result)
                else:
                    st.warning(result)
            except ValueError:
                st.error("Military ID must be a number")