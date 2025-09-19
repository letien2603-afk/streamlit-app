import streamlit as st
import pandas as pd

st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

PASSWORD = "myStrongPassword123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "full_df" not in st.session_state:
    st.session_state.full_df = None

# Password check
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

uploaded_file = st.file_uploader("Upload XLSB/XLSX file", type=["xlsb", "xlsx"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

pyxlsb_installed = True
try:
    import pyxlsb
except ImportError:
    pyxlsb_installed = False

# Read first 10 rows for preview
df_preview = pd.DataFrame()
if st.session_state.uploaded_file is not None:
    uploaded_file = st.session_state.uploaded_file
    try:
        if uploaded_file.name.endswith(".xlsb") and pyxlsb_installed:
            df_preview = pd.read_excel(uploaded_file, engine="pyxlsb", nrows=10, dtype=str)
        else:
            df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Filter input and button
search_input = st.text_input("Enter value(s) to filter (comma-separated):")

# Decide which table to display
display_df = df_preview  # default: show preview

if st.button("Filter") and search_input and st.session_state.uploaded_file is not None:
    terms = [t.strip() for t in search_input.split(",") if t.strip()]
    
    # Load full dataset if not already loaded
    if st.session_state.full_df is None:
        try:
            uploaded_file = st.session_state.uploaded_file
            if uploaded_file.name.endswith(".xlsb") and pyxlsb_installed:
                st.session_state.full_df = pd.read_excel(uploaded_file, engine="pyxlsb", dtype=str)
            else:
                st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as e:
            st.error(f"Error reading full file: {e}")
            st.stop()
    
    df_full = st.session_state.full_df
    mask = df_full.apply(
        lambda row: any(row.astype(str).str.contains(term, case=False, na=False).any() for term in terms),
        axis=1
    )
    display_df = df_full[mask]

# Show the table (preview or filtered)
if not display_df.empty:
    st.dataframe(display_df.reset_index(drop=True))
