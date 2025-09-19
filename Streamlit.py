import streamlit as st
import pandas as pd

# Hide Streamlit default menu, header, and footer
hide_streamlit_style = """
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height: 0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Set your password here
PASSWORD = "myStrongPassword123"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# Password check
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password")

# Main app
if st.session_state.logged_in:
    st.success("Welcome!")

    # File uploader
    uploaded_file = st.file_uploader("Upload a file", type=["xlsb", "xlsx"])

    df = pd.DataFrame()  # initialize df

    # Check if pyxlsb is installed
    pyxlsb_installed = True
    try:
        import pyxlsb
    except ImportError:
        pyxlsb_installed = False

    # Read uploaded file
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".xlsb"):
                if not pyxlsb_installed:
                    st.error("Missing dependency 'pyxlsb'. Please install it: pip install pyxlsb")
                else:
                    df = pd.read_excel(uploaded_file, engine='pyxlsb', dtype=str)
            else:
                df = pd.read_excel(uploaded_file, dtype=str)
            st.session_state.uploaded_df = df
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

    elif st.session_state.get("uploaded_df") is not None:
        df = st.session_state.uploaded_df

    else:
        # Fallback to default XLSB file
        if pyxlsb_installed:
            try:
                df = pd.read_excel("ATF_Streamlit.xlsb", engine='pyxlsb', dtype=str)
            except FileNotFoundError:
                st.error("Default XLSB file not found. Please upload a file.")
        else:
            st.error("Missing dependency 'pyxlsb'. Please install it: pip install pyxlsb")

    # Search and display
    if not df.empty:
        search_terms = st.text_input("Enter search keywords (comma-separated):")

        if search_terms:
            terms = [t.strip() for t in search_terms.split(",") if t.strip()]

            mask = df.apply(
                lambda row: any(row.astype(str).str.contains(term, case=False, na=False).any() for term in terms),
                axis=1
            )
            filtered_df = df[mask]

            st.write(f"Found {len(filtered_df)} matching rows:")
            st.dataframe(filtered_df.reset_index(drop=True))
        else:
            st.write("Showing first 10 rows (no filter applied):")
            st.dataframe(df.head(10).reset_index(drop=True))
    else:
        st.info("No data available. Please upload a file or check the default XLSB.")
