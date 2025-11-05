from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html
from src.common.common import page_setup

page_setup()
st.title("📊 Pmultiqc")

results_dir = Path(st.session_state.workspace, "results")
html_path = results_dir / "summarypipeline" / "multiqc_report.html"

if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")

    base_dir = html_path.parent.as_posix()
    html_content = html_content.replace(
        "<head>",
        f"<head><base href='file://{base_dir}/' target='_self'>"
    )

    block_nav = """
    <script>
    document.addEventListener('click', function(e){
        const t = e.target;
        if(t.tagName === 'A'){
            const href = t.getAttribute('href');
            if(href && href.startsWith('#')){
                e.preventDefault();
                const target = document.querySelector(href);
                if(target){
                    target.scrollIntoView();
                }
            }
        }
    }, true);
    </script>
    """

    html(html_content + block_nav, height=900, scrolling=True)

else:
    st.warning("MultiQC report not found. Please run the analysis first.")
