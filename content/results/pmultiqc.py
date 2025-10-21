from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from src.common.common import page_setup

params = page_setup()

results_dir = Path(st.session_state.workspace, "results")
html_path = results_dir /"summarypipeline" / "multiqc_report.html"

if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")
    components.html(html_content, height=800, scrolling=True)
else:
    st.warning("MultiQC report not found. Please run the analysis first.")
