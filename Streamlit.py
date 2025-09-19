import streamlit as st
import pandas as pd

# Hide Streamlit default menu, header, and footer
st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height: 0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Password setup
PASSWORD = "myStrongPassword123"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "full_df" not in st.session_state:
    st.session_state.full_df = None

# 1️⃣ Password check first
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()  # refresh app after login
        else:
            st.error("Incorrect password")
    st.stop()  # Stop here until password is entered

# 2️⃣ Main app (after login)
st.success("Welcome!")

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["xlsb", "xlsx"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

# 3️⃣ Only attempt to read file after login and upload
df_preview = pd.DataFrame()
pyxlsb_installed = True
try:
    import pyxlsb
except ImportError:
    pyxlsb_installed = False

if st.session_state.uploaded_file is not None:
    uploaded_file = st.session_state.uploaded_file
    try:
        if uploaded_file.name.endswith(".xlsb"):
            if pyxlsb_installed:
                df_preview = pd.read_excel(uploaded_file, engine="pyxlsb", nrows=10, dtype=str)
            else:
                st.error("Missing dependency 'pyxlsb'. Please install it.")
        else:
            df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
    except Exception as e:
        st.error(f"Error reading preview: {e}")

if not df_preview.empty:
    st.write("Preview (first 10 rows):")
    st.dataframe(df_preview)

# 4️⃣ Button to load full data
if st.session_state.uploaded_file is not None:
    if st.button("Load full data for filtering"):
        try:
            uploaded_file = st.session_state.uploaded_file
            if uploaded_file.name.endswith(".xlsb"):
                if pyxlsb_installed:
                    st.session_state.full_df = pd.read_excel(uploaded_file, engine="pyxlsb", dtype=str)
                else:
                    st.error("Missing dependency 'pyxlsb'. Please install it.")
            else:
                st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
            st.success("Full data loaded! You can now filter/search.")
        except Exception as e:
            st.error(f"Error reading full data: {e}")

# 5️⃣ Filtering/searching
if st.session_state.full_df is not None:
    search_terms = st.text_input("Enter search keywords (comma-separated):")
    if search_terms:
        terms = [t.strip() for t in search_terms.split(",") if t.strip()]
        mask = st.session_state.full_df.apply(
            lambda row: any(row.astype(str).str.contains(term, case=False, na=False).any() for term in terms),
            axis=1
        )
        filtered_df = st.session_state.full_df[mask]
        st.write(f"Found {len(filtered_df)} matching rows:")
        st.dataframe(filtered_df.reset_index(drop=True))
