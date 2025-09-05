from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from src.common.common import page_setup

params = page_setup()

html_path = Path("/app/results/multiqc_report.html")

html_content = html_path.read_text(encoding="utf-8")
components.html(html_content, height=800, scrolling=True)