import streamlit as st
import pandas as pd

# Hide Streamlit UI elements
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

# Password
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

# File upload
uploaded_file = st.file_uploader("Upload XLSB/XLSX file", type=["xlsb", "xlsx"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

pyxlsb_installed = True
try:
    import pyxlsb
except ImportError:
    pyxlsb_installed = False

# Filter input (only Order ID & GA08:SO TranID)
search_input = st.text_input("Enter value(s) to filter (comma-separated):")

display_df = pd.DataFrame()  # empty by default

if st.button("Filter") and search_input and uploaded_file is not None:
    terms = [t.strip() for t in search_input.split(",") if t.strip()]

    # Load full dataset only once
    if st.session_state.full_df is None:
        try:
            if uploaded_file.name.endswith(".xlsb") and pyxlsb_installed:
                st.session_state.full_df = pd.read_excel(uploaded_file, engine="pyxlsb", dtype=str)
            else:
                st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as e:
            st.error(f"Error reading full file: {e}")
            st.stop()

    df_full = st.session_state.full_df

    # Only filter on specific columns
    filter_columns = ["Order ID", "GA08:SO TranID"]
    missing_cols = [col for col in filter_columns if col not in df_full.columns]
    if missing_cols:
        st.error(f"Missing columns in the dataset: {missing_cols}")
    else:
        mask = pd.Series(False, index=df_full.index)
        for term in terms:
            mask |= df_full[filter_columns].astype(str).apply(lambda col: col.str.contains(term, case=False, na=False)).any(axis=1)

        filtered_df = df_full[mask]
        display_df = filtered_df
        st.write(f"Found {len(filtered_df)} matching rows:")

# Show filtered table only
if not display_df.empty:
    st.dataframe(display_df.reset_index(drop=True))
