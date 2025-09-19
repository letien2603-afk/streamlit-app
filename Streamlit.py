import streamlit as st
import pandas as pd
from io import BytesIO

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
# Password protection
# -----------------------------
PASSWORD = "myStrongPassword123"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

# -----------------------------
# Upload Parquet file
# -----------------------------
uploaded_file = st.file_uploader("Upload your Parquet file", type=["parquet"])

if uploaded_file is not None:
    try:
        parquet_bytes = BytesIO(uploaded_file.read())
        df = pd.read_parquet(parquet_bytes, engine="pyarrow")
        st.success(f"Loaded data ({len(df)} rows, {len(df.columns)} columns).")
    except Exception as e:
        st.error(f"Error loading Parquet file: {e}")
        st.stop()

    # -----------------------------
    # Filter box
    # -----------------------------
    search_input = st.text_input("Enter Order ID(s) or Transaction ID(s), comma-separated:")

    if st.button("Filter") and search_input:
        search_terms = [t.strip() for t in search_input.split(",") if t.strip()]
        filter_cols = ["Order ID", "GA08:SO TranID"]

        try:
            # Vectorized filtering on selected columns
            mask = df[filter_cols].apply(
                lambda col: col.str.contains("|".join(search_terms), case=False, na=False)
            ).any(axis=1)
            df_matched = df[mask]

            num_matches = len(df_matched)
            st.success(f"Found {num_matches} matching rows.")

            if num_matches > 0:
                df_display = df_matched.reset_index(drop=True)
                if num_matches <= 50:
                    # For small result sets, use st.table (all rows visible)
                    st.table(df_display)
                else:
                    # For larger result sets, use st.dataframe with scrollable height
                    table_height = min(35 * num_matches, 1000)
                    st.dataframe(df_display, height=table_height, width=1200)
            else:
                st.warning("No matching rows found.")

        except Exception as e:
            st.error(f"Error filtering data: {e}")
