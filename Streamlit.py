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

# Password setup
PASSWORD = "myStrongPassword123"

# Initialize session state
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

if st.session_state.logged_in:
    st.success("Welcome!")

    # File uploader
    uploaded_file = st.file_uploader("Upload a file", type=["xlsb", "xlsx"])

    # Check pyxlsb dependency
    pyxlsb_installed = True
    try:
        import pyxlsb
    except ImportError:
        pyxlsb_installed = False

    df_preview = pd.DataFrame()  # placeholder

    # Read uploaded file
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        try:
            if uploaded_file.name.endswith(".xlsb"):
                if not pyxlsb_installed:
                    st.error("Missing dependency 'pyxlsb'. Please install it: pip install pyxlsb")
                else:
                    df_preview = pd.read_excel(uploaded_file, engine='pyxlsb', nrows=10, dtype=str)
            else:
                df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

    elif st.session_state.uploaded_file is not None:
        # Use previously uploaded file
        uploaded_file = st.session_state.uploaded_file
        try:
            if uploaded_file.name.endswith(".xlsb"):
                if pyxlsb_installed:
                    df_preview = pd.read_excel(uploaded_file, engine='pyxlsb', nrows=10, dtype=str)
            else:
                df_preview = pd.read_excel(uploaded_file, nrows=10, dtype=str)
        except:
            pass
    else:
        st.info("Please upload a file to preview data.")

    # Show preview
    if not df_preview.empty:
        st.write("Preview (first 10 rows):")
        st.dataframe(df_preview.reset_index(drop=True))

    # Button to load full data for filtering
    if uploaded_file is not None and st.button("Load full data for filtering"):
        try:
            if uploaded_file.name.endswith(".xlsb"):
                if not pyxlsb_installed:
                    st.error("Missing dependency 'pyxlsb'. Please install it: pip install pyxlsb")
                else:
                    st.session_state.full_df = pd.read_excel(uploaded_file, engine='pyxlsb', dtype=str)
            else:
                st.session_state.full_df = pd.read_excel(uploaded_file, dtype=str)
            st.success("Full data loaded! You can now filter/search.")
        except Exception as e:
            st.error(f"Error reading full data: {e}")

    # Filtering/searching
    if st.session_state.full_df is not None:
        search_terms = st.text_input("Enter search keywords (comma-separated) for filtering:")

        if search_terms:
            terms = [t.strip() for t in search_terms.split(",") if t.strip()]
            mask = st.session_state.full_df.apply(
                lambda row: any(row.astype(str).str.contains(term, case=False, na=False).any() for term in terms),
                axis=1
            )
            filtered_df = st.session_state.full_df[mask]
            st.write(f"Found {len(filtered_df)} matching rows:")
            st.dataframe(filtered_df.reset_index(drop=True))
        else:
            st.write("Full data loaded but no filter applied yet.")
