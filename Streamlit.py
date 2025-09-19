import streamlit as st
import os

PASSWORD = os.getenv("APP_PASSWORD", "default123")

pw = st.text_input("Enter password", type="password")
if pw != PASSWORD:
    st.stop()

st.write("Welcome! You are logged in.")
