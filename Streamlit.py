import streamlit as st
import pandas as pd

# -----------------------------
# Hide Streamlit UI elements
# -----------------------------
st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Password setup
# -----------------------------
PASSWORD = "myStrongPassword123"

# -----------------------------
# Session state
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "full_df" not in st.session_state:
    st.session_state.full_df = None

# -----------------------------
# 1️⃣ Password check
# -----------------------------
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

st.success("Welcome!")

# -----------------------------
# 2️⃣ File upload
# -----------------------------
uploaded_file = st.file_uploader("Upload XLSB/XLSX file", type=["xlsb", "xlsx"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

pyxlsb_installed = True
try:
    import pyxlsb
except ImportError:
    pyxlsb_installed = False

# -----------------------------
# 3️⃣ Preview first 10 rows
# -----------------------------
df_preview = pd.DataFrame()
if st.session_state.uploaded_file is not None:
    uploaded_file = st.session_state.uploaded_file
    try:
        if uploaded_file.name.endswith(".xlsb"):
            if pyxlsb_installed:
                df_preview = pd.read_excel(uploaded_file, engine="pyxlsb", nrows=10, dtype=str)
            else:
                st.error("Missing dependency 'pyxlsb'. Please install it: pip install pyxlsb")
        else:
            df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
    except Exception as e:
        st.error(f"Error reading file: {e}")

if not df_preview.empty:
    st.write("Preview (first 10 rows):")
    st.dataframe(df_preview)

# -----------------------------
# 4️⃣ Filtering box
# -----------------------------
search_input = st.text_input("Enter value(s) to filter (comma-separated):")

if search_input and st.session_state.uploaded_file is not None:
    terms = [t.strip() for t in search_input.split(",") if t.strip()]

    # -----------------------------
    # Read full dataset only once
    # -----------------------------
    if st.session_state.full_df is None:
        try:
            uploaded_file = st.session_state.uploaded_file
            if uploaded_file.name.endswith(".xlsb") and pyxlsb_installed:
                st.session_state.full_df = pd.read_excel(uploaded_file, engine="pyxlsb", dtype=str)
            else:
                st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as e:
            st.error(f"Error reading full file for filtering: {e}")
            st.stop()

    df_full = st.session_state.full_df

    # -----------------------------
    # Filter rows containing any term in any column
    # -----------------------------
    mask = df_full.apply(
        lambda row: any(row.astype(str).str.contains(term, case=False, na=False).any() for term in terms),
        axis=1
    )
    filtered_df = df_full[mask]

    st.write(f"Found {len(filtered_df)} matching rows:")
    st.dataframe(filtered_df.reset_index(drop=True))
