import streamlit as st
import hashlib
import os
from dotenv import load_dotenv
from users_db import UsersDatabase

# Load environment variables
load_dotenv()

def authenticate(username, password):
    """Check if username and password are correct"""
    # Load admin credentials from .env
    admin_user = os.getenv('ADMIN_USERNAME')
    admin_pass = os.getenv('ADMIN_PASSWORD')
    
    if admin_user and admin_pass:  # Only check if env vars are set
        if username == admin_user and password == admin_pass:
            st.session_state.role = 'admin'
            return True
        
    db = UsersDatabase()
    if db.authenticate_user(username, password):
        user = db.users.find_one({'username': username})
        st.session_state.role = user['role']
        return True
    return False

def show_login():
    """Show login form and handle authentication"""
    st.title("Employee Management System Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

def check_auth():
    """Check if user is authenticated"""
    if not st.session_state.get('authenticated'):
        show_login()
        st.stop()  # Stop execution if not authenticated
