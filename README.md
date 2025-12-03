
import streamlit as st
import pandas as pd

# ------------------------------
# FILE UPLOADER (Changed to 2 files)
# ------------------------------
col1, col2 = st.columns(2)
mws_file = col1.file_uploader("Upload MWS file", type=["xlsx", "csv"], key="u_mws")
crt_file = col2.file_uploader("Upload CRT file", type=["xlsx", "csv"], key="u_crt")

# Helper function to read file (Polars -> Pandas)
def load_data(file):
    try:
        if file.name.lower().endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error parsing {file.name}: {e}")
        return None

# ------------------------------
# LOAD / RESET LOGIC
# ------------------------------
# Process MWS
if mws_file:
    st.session_state.mws = load_data(mws_file)
    if st.session_state.mws is not None:
        col1.success(f'MWS Loaded: {st.session_state.mws.shape}')
else:
    st.session_state.mws = None # Reset if user clicks X

# Process CRT
if crt_file:
    st.session_state.crt = load_data(crt_file)
    if st.session_state.crt is not None:
        col2.success(f'CRT Loaded: {st.session_state.crt.shape}')
else:
    st.session_state.crt = None # Reset if user clicks X
