import streamlit as st
from pathlib import Path
from src.common.common import page_setup

page_setup()

st.title("QuantMS Analysis Download Page")

if st.session_state.get("analysis_success"):
    zip_path = Path(st.session_state["results_zip_path"])
    if zip_path.exists():
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Download Results (.zip)",
                data=f,
                file_name=zip_path.name,
                mime="application/zip"
            )
    else:
        st.warning("Result zip file not found.")
else:
    st.info("Results will be available for download once the analysis is successfully completed.")