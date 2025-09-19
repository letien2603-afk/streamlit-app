import streamlit as st
import pandas as pd

# ===== Hide Streamlit UI elements =====
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

# ===== Password setup =====
PASSWORD = "myStrongPassword123"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Password input
if not st.session_state.logged_in:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()  # refresh the page
        else:
            st.error("Incorrect password")

# ===== Main app =====
if st.session_state.logged_in:
    st.success("Welcome!")

    # ===== Load CSV from Google Drive =====
    file_id = "1d90WrGEycbzltBbwpcjeksjA9CkPf0n9"
    csv_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        df = pd.read_csv(csv_url, dtype=str)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

    # ===== Search/filter functionality =====
    search_terms = st.text_input("Enter search keywords (comma-separated):")

    if search_terms:
        terms = [t.strip() for t in search_terms.split(",") if t.strip()]

        mask = df.apply(
            lambda row: any(row.astype(str).str.contains(term, case=False).any() for term in terms),
            axis=1
        )
        filtered_df = df[mask]

        st.write(f"Found {len(filtered_df)} matching rows:")
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.write("Showing first 10 rows (no filter applied):")
        st.dataframe(df.head(10).reset_index(drop=True))
