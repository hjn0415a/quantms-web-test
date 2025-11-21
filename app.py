import streamlit as st
from pathlib import Path
import json
# For some reason the windows version only works if this is imported here
import pyopenms

if "settings" not in st.session_state:
        with open("settings.json", "r") as f:
            st.session_state.settings = json.load(f)

if __name__ == '__main__':
    pages = {
        "QuantMS": [
            st.Page(Path("content", "quantms", "quickstart.py"), title="Quickstart", icon="👋"),
            st.Page(Path("content", "quantms", "generate_sdrf.py"), title="Generate SDRF", icon="📃"),
            st.Page(Path("content", "quantms", "quantms_file_upload.py"), title="Workflow", icon="⚙️"),
            st.Page(Path("content", "quantms", "quantms_download.py"), title="Download", icon="⬇️"),
        ],
        "Results": [
            #st.Page(Path("content", "results", "searchenginecomet.py"), title="Searchenginecomet", icon="🔎"),
            #st.Page(Path("content", "results", "extractpsmfeature.py"), title="Extractpsmfeature", icon="🧩"),
            #st.Page(Path("content", "results", "psmclean.py"), title="PSMclean", icon="🧹"),
            #st.Page(Path("content", "results", "percolator.py"), title="Percolator", icon="⚡"),
            #st.Page(Path("content", "results", "idscoreswitcher.py"), title="Idscoreswitcher", icon="🔄"),
            st.Page(Path("content", "results", "idfilter.py"), title="Peptide Spectrum Matches (PSMs)", icon="🔍"),
            st.Page(Path("content", "results", "proteomicslfq.py"), title="Quantification Results", icon="📊"),
            st.Page(Path("content", "results", "msstats.py"), title="Statistical Analysis", icon="📈"),
            st.Page(Path("content", "results", "pmultiqc.py"), title="Quality Control", icon="📃"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()