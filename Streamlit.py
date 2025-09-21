import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="ATF App",                 
    layout="wide"                    
)

# -----------------------------
# Hide Streamlit UI elements and remove top padding
# -----------------------------
st.markdown("""
<style>
/* Hide default Streamlit header/footer */
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}

/* Remove top padding / margin */
.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Password protection
# -----------------------------
PASSWORD = "Callidus123"
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

# -----------------------------
# Welcome message with week of month
# -----------------------------
today = datetime.today()
first_day = today.replace(day=1)
week_of_month = (today.day + first_day.weekday()) // 7 + 1
month_name = today.strftime("%B")

st.success(f"Welcome to the ATF file - **Week {week_of_month} of {month_name}**.")

# -----------------------------
# Upload Parquet file
# -----------------------------
uploaded_file = st.file_uploader("Upload the ATF Parquet file", type=["parquet"])

if uploaded_file is not None:
    try:
        parquet_bytes = BytesIO(uploaded_file.read())
        df = pd.read_parquet(parquet_bytes, engine="pyarrow")
        st.success(f"Loaded data ({len(df)} rows, {len(df.columns)} columns).")
    except Exception as e:
        st.error(f"Error loading Parquet file: {e}")
        st.stop()

    # -----------------------------
    # Full ATF Access
    # -----------------------------
    st.subheader("Full ATF Access")
    if st.button("Show Google Drive Link for Full ATF"):
        st.markdown(
            '[Click here to access the Full ATF on Google Drive](https://drive.google.com/your-folder-link)',
            unsafe_allow_html=True
        )

    # -----------------------------
    # Section: Month Slicer (independent filter)
    # -----------------------------
    st.subheader("Filter by Month")

    with st.form("form_month"):
    if "Month" in df.columns:
        month_options = sorted(df["Month"].dropna().unique())
        selected_months = st.multiselect("Select Month(s):", month_options)
        submit_month = st.form_submit_button("Filter Month(s)")

        if submit_month:
            if selected_months:
                df_month_filtered = df[df["Month"].isin(selected_months)]
                if not df_month_filtered.empty:
                    st.success(f"Found {len(df_month_filtered)} rows for selected Month(s).")
                    st.dataframe(df_month_filtered.head(11).reset_index(drop=True))
                    csv_data_month = df_month_filtered.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Month Filtered Rows to CSV",
                        csv_data_month,
                        "matched_rows_month.csv",
                        "text/csv"
                    )
                else:
                    st.warning("No matching rows found for the selected Month(s).")
            else:
                st.warning("Please select at least one Month before clicking Filter.")
    else:
        st.warning("No 'Month' column found in the uploaded file.")


    # -----------------------------
    # Section 1: Filter by IDs
    # -----------------------------
    st.subheader("Filter IDs")
    with st.form("form_ids"):
        search_input_ids = st.text_input(
            "Enter Order ID, GA08:SO TranID, PO Number, GA24: Distribution Sold to System Integrator ID, Billing Customer ID, Other Customer ID (comma-separated):"
        )
        submit_ids = st.form_submit_button("Filter IDs")

    if submit_ids:
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
            for col in filter_cols_ids:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            mask_ids = df[filter_cols_ids].apply(
                lambda col: col.str.contains("|".join(search_terms_ids), case=False, na=False)
            ).any(axis=1)

            df_matched_ids = df[mask_ids]

            if not df_matched_ids.empty:
                st.success(f"Found {len(df_matched_ids)} matching rows for Section 1.")
                st.dataframe(df_matched_ids.head(11).reset_index(drop=True))
                csv_data_ids = df_matched_ids.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Matched IDs to CSV",
                    csv_data_ids,
                    "matched_rows_section1.csv",
                    "text/csv"
                )
            else:
                st.warning("No matching rows found in Section 1.")

    # -----------------------------
    # Section 2: Filter by Names / Products
    # -----------------------------
    st.subheader("Filter Names / Products")
    with st.form("form_names"):
        search_input_names = st.text_input(
            "Enter GA25: Distribution Sold to System Integrator Name, Billing Company, Other Company, Product ID (comma-separated):"
        )
        submit_names = st.form_submit_button("Filter Names/Products")

    if submit_names:
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
            for col in filter_cols_names:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            mask_names = df[filter_cols_names].apply(
                lambda col: col.str.contains("|".join(search_terms_names), case=False, na=False)
            ).any(axis=1)

            df_matched_names = df[mask_names]

            if not df_matched_names.empty:
                st.success(f"Found {len(df_matched_names)} matching rows for Section 2.")
                st.dataframe(df_matched_names.head(11).reset_index(drop=True))
                csv_data_names = df_matched_names.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Matched Names/Products to CSV",
                    csv_data_names,
                    "matched_rows_section2.csv",
                    "text/csv"
                )
            else:
                st.warning("No matching rows found in Section 2.")
