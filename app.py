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
             st.Page(Path("content", "quantms", "quantms_file_upload.py"), title="Workflow", icon="⚙️"),
             st.Page(Path("content", "quantms", "quantms_download.py"), title="Download", icon="⬇️"),
             st.Page(Path("content", "quantms", "generate_sdrf.py"), title="Generate SDRF", icon="📃"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()