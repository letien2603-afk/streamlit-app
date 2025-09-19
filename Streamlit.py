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
            st.rerun()
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
    # Section 1: Filter by IDs
    # -----------------------------
    st.subheader("Filter Section 1: IDs")
    search_input_ids = st.text_input(
        "Enter Order ID, GA08:SO TranID, PO Number, GA24: Distribution Sold to System Integrator ID, Billing Customer ID, Other Customer ID (comma-separated):"
    )

    if st.button("Filter by IDs"):
        if search_input_ids.strip() == "":
            st.warning("Please enter at least one search term for Section 1.")
        else:
            search_terms_ids = [t.strip() for t in search_input_ids.split(",") if t.strip()]
            filter_cols_ids = [
                "Order ID",
                "GA08:SO TranID",
                "PO Number",
                "GA24: Distribution Sold to System Integrator ID",
                "Billing Customer ID",
                "Other Customer ID"
            ]
            # Convert columns to string to prevent crashes
            for col in filter_cols_ids:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            mask_ids = df[filter_cols_ids].apply(
                lambda col: col.str.contains("|".join(search_terms_ids), case=False, na=False)
            ).any(axis=1)
            df_matched_ids = df[mask_ids]

            if not df_matched_ids.empty:
                st.success(f"Found {len(df_matched_ids)} matching rows for Section 1.")
                st.dataframe(df_matched_ids.reset_index(drop=True), height=500, width=1200)
                csv_data_ids = df_matched_ids.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Section 1 matched rows as CSV",
                    csv_data_ids,
                    "matched_rows_section1.csv",
                    "text/csv"
                )
            else:
                st.warning("No matching rows found in Section 1.")

    # -----------------------------
    # Section 2: Filter by Names / Products
    # -----------------------------
    st.subheader("Filter Section 2: Names / Products")
    search_input_names = st.text_input(
        "Enter GA25: Distribution Sold to System Integrator Name, Billing Company, Other Company, Product ID (comma-separated):"
    )

    if st.button("Filter by Names/Products"):
        if search_input_names.strip() == "":
            st.warning("Please enter at least one search term for Section 2.")
        else:
            search_terms_names = [t.strip() for t in search_input_names.split(",") if t.strip()]
            filter_cols_names = [
                "GA25: Distribution Sold to System Integrator Name",
                "Billing Company",
                "Other Company",
                "Product ID"
            ]
            # Convert columns to string to prevent crashes
            for col in filter_cols_names:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            mask_names = df[filter_cols_names].apply(
                lambda col: col.str.contains("|".join(search_terms_names), case=False, na=False)
            ).any(axis=1)
            df_matched_names = df[mask_names]

            if not df_matched_names.empty:
                st.success(f"Found {len(df_matched_names)} matching rows for Section 2.")
                st.dataframe(df_matched_names.reset_index(drop=True), height=500, width=1200)
                csv_data_names = df_matched_names.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Section 2 matched rows as CSV",
                    csv_data_names,
                    "matched_rows_section2.csv",
                    "text/csv"
                )
            else:
                st.warning("No matching rows found in Section 2.")
