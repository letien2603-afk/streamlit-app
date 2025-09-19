import streamlit as st
import pandas as pd

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
            st.rerun()  # refresh the page
        else:
            st.error("Incorrect password")

# If logged in, show CSV preview
if st.session_state.logged_in:
    st.success("Welcome!")

    # Load CSV file (make sure 'data.csv' is in the same folder as Streamlit.py)
    df = pd.read_csv("ATF_Streamlit.csv")

    # Show only first 10 rows
    st.write("Here are the first 10 rows from the CSV:")
    st.dataframe(df.head(10))
