import streamlit as st
from pathlib import Path
from src.common.common import page_setup

page_setup()

st.title("QuantMS Analysis Download Page")

results_dir = Path(st.session_state.workspace, "results")
zip_path = results_dir.with_suffix(".zip")

if zip_path.is_file():
    with open(zip_path, "rb") as f:
        st.download_button(
            label="📦 Download Results (.zip)",
            data=f,
            file_name=zip_path.name,
            mime="application/zip"
        )
else:
    st.info("Results will be available for download once the analysis is successfully completed.")