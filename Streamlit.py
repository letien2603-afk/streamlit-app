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
# Helper: Convert DataFrame to CSV safely
# -----------------------------
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    # Replace None/NaN with empty string and keep as str
    df_clean = df.fillna("").astype(str).replace("None", "")
    return df_clean.to_csv(index=False, quoting=1).encode("utf-8")

# -----------------------------
# Cached filter for performance
# -----------------------------
@st.cache_data
def filter_by_month(df, selected_months):
    return df[df["Month"].isin(selected_months)]

# -----------------------------
# Welcome message with week of month
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
        '[Click here to access the Full ATF on Google Drive](https://drive.google.com/file/d/13soYzyXK9S8MuAhpPSyDc-o9jNDVuT5X/view?usp=drive_link)',
        unsafe_allow_html=True
    )
        
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
    # Section: Month Slicer
    # -----------------------------
    st.subheader("Filter by Month")
    df_month_filtered = pd.DataFrame()
    if "Month" in df.columns:
        with st.form("form_month"):
            month_options = sorted(df["Month"].dropna().unique())
            selected_months = st.multiselect("Select Month(s):", month_options)
            submit_month = st.form_submit_button("Filter Month(s)")

        if submit_month:
            if selected_months:
                df_month_filtered = filter_by_month(df, selected_months)
                if not df_month_filtered.empty:
                    st.success(f"Found {len(df_month_filtered)} rows for selected Month(s).")

                    # ✅ Only preview 11 rows if small enough
                    if len(df_month_filtered) <= 50_000:
                        st.dataframe(df_month_filtered.head(11).reset_index(drop=True))
                    else:
                        st.info("Large dataset (>50k rows). Skipping preview to save memory.")

                    # ✅ Always allow full CSV download
                    csv_data_month = convert_df_to_csv(df_month_filtered)
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
