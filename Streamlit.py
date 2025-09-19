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
    st.error("Missing 'pyxlsb'. Install with: pip install pyxlsb")
    st.stop()

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

if uploaded_file is not None:
    file_bytes = BytesIO(uploaded_file.read())

    st.info("Please enter the values you want to filter.")

    search_input = st.text_input("Enter Order ID(s) or Transaction ID(s), comma-separated:")

    if st.button("Filter") and search_input:
        search_terms = [t.strip() for t in search_input.split(",") if t.strip()]

        try:
            st.info("Scanning XLSB for matching rows (fast, streaming)...")

            matched_rows = []
            with open_workbook(file_bytes) as wb:
                sheet = wb.get_sheet(1)
                header_row = next(sheet.rows())
                header = [cell.v for cell in header_row]
                filter_cols = ["Order ID", "GA08:SO TranID"]

                # Ensure filter columns exist
                col_indices = [header.index(col) for col in filter_cols]

                # Stream-read XLSB and store only matching rows
                for i, row in enumerate(sheet.rows()):
                    values = [row[j].v if row[j].v is not None else "" for j in col_indices]
                    if any(str(val) in search_terms for val in values):
                        # Store full row
                        full_row = [row[k].v if row[k].v is not None else "" for k in range(len(header))]
                        matched_rows.append(full_row)

            if matched_rows:
                df_matched = pd.DataFrame(matched_rows, columns=header).astype(str)
                st.success(f"Found {len(df_matched)} matching rows.")

                # Display matched rows
                st.dataframe(df_matched.reset_index(drop=True), height=500, width=1200)

                # Download option
                csv_data = df_matched.to_csv(index=False).encode("utf-8")
                st.download_button("Download matched rows as CSV", csv_data, "matched_rows.csv", "text/csv")
            else:
                st.warning("No matching rows found.")

        except Exception as e:
            st.error(f"Error processing XLSB: {e}")
