import streamlit as st
import pandas as pd

hide_streamlit_style = """
<style>
/* Hide footer including "Manage app" */
footer[data-testid="stAppFooter"] {
    visibility: hidden;
    height: 0px;
}

/* Hide hamburger menu */
#MainMenu {visibility: hidden;}

/* Hide header */
header {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Set your password here
PASSWORD = "myStrongPassword123"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If not logged in, show password input
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()  # refresh the page
        else:
            st.error("Incorrect password")

# If logged in, show CSV preview with filter option
if st.session_state.logged_in:
    st.success("Welcome!")

    # ===== Load CSV from Google Drive =====
    # Use the "shareable link" of your Google Drive CSV file
    # Example link: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    # Convert to direct download link:
    file_id = "1d90WrUEycbzltBbwpcjeksjA9CkPf0n9"
    csv_url = f"https://drive.google.com/uc?id={file_id}"

    # Read CSV
    df = pd.read_csv(csv_url, dtype=str)

    # Search input
    search_terms = st.text_input("Enter search keywords (comma-separated):")

    if search_terms:
        # Split input into list of terms, strip spaces
        terms = [t.strip() for t in search_terms.split(",") if t.strip()]

        # Create a mask for rows matching any term across all columns
        mask = df.apply(
            lambda row: any(row.astype(str).str.contains(term, case=False).any() for term in terms),
            axis=1
        )
        filtered_df = df[mask]

        st.write(f"Found {len(filtered_df)} matching rows:")

        # Reset index so no extra index column shows
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.write("Showing first 10 rows (no filter applied):")
        st.dataframe(df.head(10).reset_index(drop=True))
