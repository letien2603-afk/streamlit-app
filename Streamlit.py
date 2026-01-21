import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="ATF App", layout="wide")

# -----------------------------
# Hide Streamlit UI elements and remove top padding
# -----------------------------
st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
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
# Helper: Convert DataFrame to Excel using xlsxwriter
# -----------------------------
@st.cache_data(ttl=600)
def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# -----------------------------
# Welcome message
# -----------------------------
today = datetime.today()
first_day = today.replace(day=1)
week_of_month = (today.day + first_day.weekday()) // 7 + 1
month_name = today.strftime("%B")
st.success(f"Welcome to the ATF file - **Week {week_of_month} of {month_name}**.")

# -----------------------------
# Full ATF Access
# -----------------------------
st.subheader("Full ATF Access")
if st.button("Show Google Drive Link for Full ATF"):
    st.markdown(
        '[Click here to access the Full ATF on Google Drive](https://drive.google.com/file/d/1qlsl6PBbSTZOcQ8nEXz4tWtNR0_3UAt8/view?usp=drive_link)',
        unsafe_allow_html=True
    )

# -----------------------------
# Upload Parquet file
# -----------------------------
uploaded_file = st.file_uploader("Upload the ATF Parquet file", type=["parquet"])

if uploaded_file is not None and "df" not in st.session_state:
    try:
        df = pd.read_parquet(uploaded_file, engine="pyarrow")
        st.session_state.df = df
        st.success(f"Loaded data ({len(df)} rows, {len(df.columns)} columns).")
    except Exception as e:
        st.error(f"Error loading Parquet file: {e}")
        st.stop()

# -----------------------------
# Filtering Sections
# -----------------------------
if "df" in st.session_state:
    df = st.session_state.df

    # Section 1: Filter by IDs
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

            st.session_state.df_matched_ids = df[mask_ids]

    if "df_matched_ids" in st.session_state and not st.session_state.df_matched_ids.empty:
        df_matched_ids = st.session_state.df_matched_ids
        st.success(f"Found {len(df_matched_ids)} matching rows for Section 1.")
        st.dataframe(df_matched_ids.head(11).reset_index(drop=True))

        df_limited_ids = df_matched_ids.head(10000)
        excel_data_ids = convert_df_to_excel(df_limited_ids)

        st.download_button(
            "Download to Excel-XLSX",
            excel_data_ids,
            "matched_rows_section1.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Section 2: Filter Names / Products
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

            st.session_state.df_matched_names = df[mask_names]

    if "df_matched_names" in st.session_state and not st.session_state.df_matched_names.empty:
        df_matched_names = st.session_state.df_matched_names
        st.success(f"Found {len(df_matched_names)} matching rows for Section 2.")
        st.dataframe(df_matched_names.head(11).reset_index(drop=True))

        df_limited_names = df_matched_names.head(10000)
        excel_data_names = convert_df_to_excel(df_limited_names)

        st.download_button(
            "Download Matched Names/Products to Excel",
            excel_data_names,
            "matched_rows_section2.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
