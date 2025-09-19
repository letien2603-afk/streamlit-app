import streamlit as st
import pandas as pd
from io import BytesIO

# Check for pyxlsb if XLSB files will be used
try:
    import pyxlsb
    PYXLSB_AVAILABLE = True
except ImportError:
    PYXLSB_AVAILABLE = False

# Hide Streamlit UI elements
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
# File upload
# -----------------------------
uploaded_file = st.file_uploader("Upload XLSB/XLSX file", type=["xlsb", "xlsx"])

# -----------------------------
# Search input
# -----------------------------
search_input = st.text_input("Enter Order ID(s) to filter (comma-separated):")

# Only filter when button is clicked
if st.button("Filter") and uploaded_file is not None and search_input:
    search_terms = [t.strip() for t in search_input.split(",") if t.strip()]
    matched_rows = []

    try:
        # XLSB file
        if uploaded_file.name.endswith(".xlsb"):
            if not PYXLSB_AVAILABLE:
                st.error("Missing 'pyxlsb' package. Install with: pip install pyxlsb")
                st.stop()

            from pyxlsb import open_workbook
            file_bytes = BytesIO(uploaded_file.read())
            with open_workbook(file_bytes) as wb:
                sheet = wb.get_sheet(1)  # first sheet
                header_row = next(sheet.rows())
                header = [cell.v for cell in header_row]

                # Get indexes of the filter columns
                try:
                    order_id_idx = header.index("Order ID")
                    so_tranid_idx = header.index("GA08:SO TranID")
                except ValueError as e:
                    st.error(f"Column not found: {e}")
                    st.stop()

                # Iterate rows and keep only matches
                for row in sheet.rows():
                    row_values = [cell.v if cell.v is not None else "" for cell in row]
                    if str(row_values[order_id_idx]) in search_terms or str(row_values[so_tranid_idx]) in search_terms:
                        matched_rows.append(row_values)

        # XLSX file
        else:
            df_full = pd.read_excel(uploaded_file, dtype=str)
            filter_columns = ["Order ID", "GA08:SO TranID"]
            missing_cols = [col for col in filter_columns if col not in df_full.columns]
            if missing_cols:
                st.error(f"Missing columns in the dataset: {missing_cols}")
                st.stop()

            mask = pd.Series(False, index=df_full.index)
            for term in search_terms:
                mask |= df_full[filter_columns].astype(str).apply(
                    lambda col: col.str.contains(term, case=False, na=False)
                ).any(axis=1)
            df_filtered = df_full[mask]
            matched_rows = df_filtered.values.tolist()
            header = df_full.columns.tolist()

        # Show results
        if matched_rows:
            df_result = pd.DataFrame(matched_rows, columns=header)
            st.write(f"Found {len(df_result)} matching rows:")
            st.dataframe(df_result)
        else:
            st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
