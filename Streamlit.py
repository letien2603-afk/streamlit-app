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
# Cache reading XLSB filter columns
# -----------------------------
@st.cache_data
def read_filter_columns(file_bytes, filter_cols):
    with open_workbook(file_bytes) as wb:
        sheet = wb.get_sheet(1)
        header_row = next(sheet.rows())
        header = [cell.v for cell in header_row]

        # Ensure filter columns exist
        col_indices = [header.index(col) for col in filter_cols]

        # Read only filter columns
        rows = [[row[i].v if row[i].v is not None else "" for i in col_indices] for row in sheet.rows()]

    df_filter = pd.DataFrame(rows, columns=filter_cols).astype(str)
    return df_filter, header

# -----------------------------
# Cache reading matched rows fully
# -----------------------------
@st.cache_data
def read_matched_rows(file_bytes, matched_indices, all_columns):
    with open_workbook(file_bytes) as wb:
        sheet = wb.get_sheet(1)
        rows = []
        for i, row in enumerate(sheet.rows()):
            if i in matched_indices:
                rows.append([cell.v if cell.v is not None else "" for cell in row])
    df_matched = pd.DataFrame(rows, columns=all_columns).astype(str)
    return df_matched

# -----------------------------
# Main processing
# -----------------------------
if uploaded_file is not None:
    if pyxlsb is None:
        st.error("Missing 'pyxlsb'. Install with: pip install pyxlsb")
        st.stop()

    st.info("Reading filter columns (fast)...")
    file_bytes = BytesIO(uploaded_file.read())
    filter_columns = ["Order ID", "GA08:SO TranID"]

    try:
        df_filter, all_columns = read_filter_columns(file_bytes, filter_columns)

        search_input = st.text_input("Enter Order ID(s) to filter (comma-separated):")

        if st.button("Filter") and search_input:
            search_terms = [t.strip() for t in search_input.split(",") if t.strip()]

            # Vectorized filtering on filter columns
            mask = df_filter.apply(
                lambda col: col.str.contains("|".join(search_terms), case=False, na=False)
            ).any(axis=1)

            matched_indices = df_filter[mask].index.tolist()

            if matched_indices:
                st.info(f"Found {len(matched_indices)} matching rows. Loading full data for these rows...")

                df_matched = read_matched_rows(file_bytes, matched_indices, all_columns)

                st.write(f"Showing {len(df_matched)} matched rows (all columns):")
                st.dataframe(df_matched.reset_index(drop=True))
            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error processing XLSB file: {e}")
