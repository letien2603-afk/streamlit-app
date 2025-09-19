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
# Cache conversion to Parquet
# -----------------------------
@st.cache_data
def convert_xlsb_to_parquet(file_bytes):
    if pyxlsb is None:
        raise ImportError("Missing 'pyxlsb'. Install with: pip install pyxlsb")

    with open_workbook(file_bytes) as wb:
        sheet = wb.get_sheet(1)  # first sheet
        header_row = next(sheet.rows())
        header = [cell.v for cell in header_row]

        # Only needed columns
        needed_columns = ["Order ID", "GA08:SO TranID"]
        col_indices = [header.index(col) for col in needed_columns]

        # Read only needed columns
        rows = []
        for row in sheet.rows():
            rows.append([row[i].v if row[i].v is not None else "" for i in col_indices])

    df_needed = pd.DataFrame(rows, columns=needed_columns)

    # Convert all columns to strings to prevent ArrowTypeError
    df_needed = df_needed.astype(str)

    # Convert to Parquet in memory
    parquet_buffer = BytesIO()
    df_needed.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    return pd.read_parquet(parquet_buffer)

# -----------------------------
# Filter input
# -----------------------------
if uploaded_file is not None:
    st.info("Converting XLSB to Parquet for fast filtering (only needed columns)...")
    file_bytes = BytesIO(uploaded_file.read())

    try:
        df_parquet = convert_xlsb_to_parquet(file_bytes)
        st.success("Conversion complete! Ready for filtering.")

        # Search input
        search_input = st.text_input("Enter Order ID(s) to filter (comma-separated):")

        if st.button("Filter") and search_input:
            search_terms = [t.strip() for t in search_input.split(",") if t.strip()]

            # Filter rows
            mask = df_parquet.astype(str).apply(
                lambda col: col.str.contains("|".join(search_terms), case=False, na=False)
            ).any(axis=1)

            filtered_df = df_parquet[mask]

            if not filtered_df.empty:
                st.write(f"Found {len(filtered_df)} matching rows:")
                st.dataframe(filtered_df.reset_index(drop=True))
            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error processing XLSB file: {e}")
