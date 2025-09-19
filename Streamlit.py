import streamlit as st
import pandas as pd
from io import BytesIO

# -----------------------------
# Check for pyxlsb
# -----------------------------
try:
    import pyxlsb
    from pyxlsb import open_workbook
except ImportError:
    pyxlsb = None

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
# Upload XLSB file
# -----------------------------
uploaded_file = st.file_uploader("Upload XLSB file", type=["xlsb"])

# -----------------------------
# Convert XLSB to Parquet immediately after upload
# -----------------------------
if uploaded_file is not None:
    if pyxlsb is None:
        st.error("Missing 'pyxlsb'. Install with: pip install pyxlsb")
        st.stop()

    st.info("Converting XLSB to Parquet for fast filtering...")

    file_bytes = BytesIO(uploaded_file.read())
    with open_workbook(file_bytes) as wb:
        sheet = wb.get_sheet(1)  # first sheet
        header_row = next(sheet.rows())
        header = [cell.v for cell in header_row]
        rows = [[cell.v if cell.v is not None else "" for cell in r] for r in sheet.rows()]

    df = pd.DataFrame(rows, columns=header)

    # Convert to Parquet in memory
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)
    st.success("Conversion complete! Ready for filtering.")

    # Keep Parquet in memory
    df_parquet = pd.read_parquet(parquet_buffer)

    # -----------------------------
    # Filter input
    # -----------------------------
    search_input = st.text_input("Enter Order ID(s) to filter (comma-separated):")

    if st.button("Filter") and search_input:
        search_terms = [t.strip() for t in search_input.split(",") if t.strip()]

        # Ensure required columns exist
        filter_columns = ["Order ID", "GA08:SO TranID"]
        missing_cols = [col for col in filter_columns if col not in df_parquet.columns]
        if missing_cols:
            st.error(f"Missing columns in the dataset: {missing_cols}")
            st.stop()

        # Filter rows
        mask = df_parquet[filter_columns].astype(str).apply(
            lambda col: col.str.contains("|".join(search_terms), case=False, na=False)
        ).any(axis=1)

        filtered_df = df_parquet[mask]

        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} matching rows:")
            st.dataframe(filtered_df.reset_index(drop=True))
        else:
            st.warning("No matching rows found.")
