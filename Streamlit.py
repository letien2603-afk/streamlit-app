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
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv", "xlsx"])

    # If a file is uploaded, read it
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
        else:
            df = pd.read_excel(uploaded_file, dtype=str)
        st.session_state.uploaded_df = df  # store in session state
    elif st.session_state.uploaded_df is not None:
        # Use previously uploaded file if page reruns
        df = st.session_state.uploaded_df
    #else:
        # Fallback to default CSV if no file uploaded
        #df = pd.read_csv("ATF_Streamlit.csv", dtype=str)
        #st.info("Using default CSV file")

    # Search input
    search_terms = st.text_input("Enter search keywords (comma-separated):")

    if search_terms:
        # Split input into list of terms, strip spaces
        terms = [t.strip() for t in search_terms.split(",") if t.strip()]

        # Filter rows that match any term in any column
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
