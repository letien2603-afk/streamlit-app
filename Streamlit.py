import streamlit as st
import pandas as pd

# Hide Streamlit UI
st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

PASSWORD = "myStrongPassword123"

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "full_df" not in st.session_state:
    st.session_state.full_df = None

# 1️⃣ Password check
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
    st.stop()

st.success("Welcome!")

# 2️⃣ File upload
uploaded_file = st.file_uploader("Upload XLSB/XLSX file", type=["xlsb", "xlsx"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

pyxlsb_installed = True
try:
    import pyxlsb
except ImportError:
    pyxlsb_installed = False

df_preview = pd.DataFrame()

# 3️⃣ Preview
if st.session_state.uploaded_file is not None:
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file.name.endswith(".xlsb"):
        if pyxlsb_installed:
            try:
                # Only read headers (very fast)
                df_preview = pd.read_excel(uploaded_file, engine="pyxlsb", nrows=0)
                st.write("Columns detected:", list(df_preview.columns))
                st.info("Preview of XLSB data is disabled for speed. Load full data to filter.")
            except Exception as e:
                st.error(f"Error reading XLSB headers: {e}")
        else:
            st.error("Missing dependency 'pyxlsb'. Please install it.")
    else:
        try:
            df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
            st.write("Preview (first 10 rows):")
            st.dataframe(df_preview)
        except Exception as e:
            st.error(f"Error reading XLSX preview: {e}")

# 4️⃣ Load full data
if st.session_state.uploaded_file is not None and st.button("Load full data for filtering"):
    try:
        uploaded_file = st.session_state.uploaded_file
        if uploaded_file.name.endswith(".xlsb") and pyxlsb_installed:
            st.session_state.full_df = pd.read_excel(uploaded_file, engine="pyxlsb", dtype=str)
        else:
            st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
        st.success("Full data loaded! You can now filter/search.")
    except Exception as e:
        st.error(f"Error loading full data: {e}")

# 5️⃣ Multi-value filtering
if st.session_state.full_df is not None:
    df = st.session_state.full_df

    # Select column to filter
    col_to_filter = st.selectbox("Select column to filter:", options=df.columns)

    # Multi-select values in that column
    unique_values = df[col_to_filter].dropna().unique()
    selected_values = st.multiselect("Select value(s) to filter:", options=unique_values)

    if selected_values:
        filtered_df = df[df[col_to_filter].isin(selected_values)]
        st.write(f"Found {len(filtered_df)} matching rows:")
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.write("No filter applied yet. Showing full dataset.")
        st.dataframe(df.head(10))  # show first 10 rows as default
