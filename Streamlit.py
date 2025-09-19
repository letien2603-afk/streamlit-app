import streamlit as st
import pandas as pd

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

    # Load CSV
    df = pd.read_csv("ATF_Streamlit.csv")

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
