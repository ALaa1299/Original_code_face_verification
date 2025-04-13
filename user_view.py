import streamlit as st
from users_db import UsersDatabase

def show():
    """User management interface for admin"""
    st.header("User Management")
    db = UsersDatabase()

    # Only allow admin access
    if st.session_state.get('role') != 'admin':
        st.error("Only administrators can access this page")
        return

    # Create new user form
    with st.expander("Create New User"):
        with st.form("create_user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            submitted = st.form_submit_button("Create User")
            
            if submitted:
                try:
                    if db.create_user(username, password, role):
                        st.success(f"User {username} created successfully")
                        st.experimental_rerun()  # Refresh the user list
                    else:
                        st.error("Username already exists or invalid input")
                except Exception as e:
                    st.error(f"Error creating user: {str(e)}")

    # User list and management
    with st.expander("Existing Users"):
        users = db.get_all_users()
        
        if not users:
            st.info("No users found")
            return
            
        for user in users:
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.write(f"**{user['username']}** (Role: {user['role']})")
            with cols[2]:
                if st.button("Delete", key=f"del_{user['username']}"):
                    try:
                        if db.delete_user(user['username']):
                            st.success(f"Deleted user {user['username']}")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete user")
                    except Exception as e:
                        st.error(f"Error deleting user: {str(e)}")