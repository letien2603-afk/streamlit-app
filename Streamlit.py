import streamlit as st
import pandas as pd
from pyxlsb import open_workbook
from io import BytesIO

st.markdown("""
<style>
footer[data-testid="stAppFooter"] {visibility: hidden; height:0px;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

PASSWORD = "myStrongPassword123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Password
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

uploaded_file = st.file_uploader("Upload XLSB file", type=["xlsb"])
search_input = st.text_input("Enter Order ID(s) to filter (comma-separated):")

if st.button("Filter") and uploaded_file is not None and search_input:
    search_terms = [t.strip() for t in search_input.split(",") if t.strip()]
    matched_rows = []

    try:
        # Convert UploadedFile to BytesIO
        file_bytes = BytesIO(uploaded_file.read())

        with open_workbook(file_bytes) as wb:
            sheet = wb.get_sheet(1)  # first sheet
            header_row = next(sheet.rows())
            header = [cell.v for cell in header_row]

            # Get indexes for filtering columns
            try:
                order_id_idx = header.index("Order ID")
                so_tranid_idx = header.index("GA08:SO TranID")
            except ValueError as e:
                st.error(f"Column not found: {e}")
                st.stop()

            # Iterate rows and collect matches
            for row in sheet.rows():
                row_values = [cell.v if cell.v is not None else "" for cell in row]
                if any(str(row_values[order_id_idx]) in search_terms or str(row_values[so_tranid_idx]) in search_terms):
                    matched_rows.append(row_values)

        if matched_rows:
            df_result = pd.DataFrame(matched_rows, columns=header)
            st.write(f"Found {len(df_result)} matching rows:")
            st.dataframe(df_result)
        else:
            st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error processing XLSB: {e}")
