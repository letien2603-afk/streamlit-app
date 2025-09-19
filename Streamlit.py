import streamlit as st

# Set your password here
PASSWORD = "myStrongPassword123"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If not logged in, show password input
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()  # refresh the page
        else:
            st.error("Incorrect password")

# If logged in, show welcome message
if st.session_state.logged_in:
    st.success("Welcome!")
