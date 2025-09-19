import streamlit as st
import os

# Read password from secrets
PASSWORD = st.secrets["APP_PASSWORD"]

pw = st.text_input("Enter password", type="password")

if pw != PASSWORD:
    st.stop()

st.success("✅ Welcome! You are logged in.")