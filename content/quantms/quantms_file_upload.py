from pathlib import Path
import streamlit as st
import pandas as pd
import zipfile

from src.common.common import (
    page_setup,
    save_params,
    v_space,
    show_table,
    TK_AVAILABLE,
    tk_directory_dialog,
)
from src.upload import sdrf_upload, fasta_upload
from src.workflow.CommandExecutor import CommandExecutor

def zip_results_folder(results_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in results_dir.rglob("*"):
            zipf.write(file, arcname=file.relative_to(results_dir))

params = page_setup()

st.title("QuantMS Analysis Web Interface (Nextflow-Based)")

# Create tabs
tabs = st.tabs(["📁 File Upload", "⚙️ Configure", "🚀 Run"])

# Define directories
sdrf_dir = Path(st.session_state.workspace, "sdrf-files")
sdrf_dir.mkdir(parents=True, exist_ok=True)

fasta_dir = Path(st.session_state.workspace, "fasta-files")
fasta_dir.mkdir(parents=True, exist_ok=True)

# --------- TAB 1: File Upload ---------
with tabs[0]:
    sub_tabs = st.tabs(["Input", "Database"])

# SDRF Upload Tab
with sub_tabs[0]:
    st.markdown("#### 🔼 Option 1: Upload SDRF Files Directly")
    with st.form("sdrf-upload", clear_on_submit=True):
        files = st.file_uploader(
            "Upload SDRF files", type=["sdrf", "tsv"],
            accept_multiple_files=(st.session_state.location == "local")
        )
        if st.form_submit_button("Add SDRF files", type="primary"):
            if files:
                sdrf_upload.save_uploaded_sdrf(files)
            else:
                st.warning("Please select SDRF files.")

    st.markdown("---")

    st.markdown("#### 📁 Option 2: Import SDRF Files from Local Folder")
    if st.session_state.location == "local":
        if st.button("📁 Browse SDRF folder", disabled=not TK_AVAILABLE):
            st.session_state["local_sdrf_dir"] = tk_directory_dialog("Select SDRF directory", st.session_state["previous_dir"])
            st.session_state["previous_dir"] = st.session_state["local_sdrf_dir"]

        local_sdrf_dir = st.text_input("Path to SDRF folder", value=st.session_state.get("local_sdrf_dir", ""))
        if st.button("Copy SDRF files", disabled=(local_sdrf_dir == "")):
            use_copy = st.checkbox("Copy files", key="sdrf_copy", value=True)
            if not use_copy:
                st.warning("Using original files. Ensure paths remain valid.")
            sdrf_upload.copy_local_sdrf_files_from_directory(local_sdrf_dir, use_copy)

    # Show SDRF files in workspace
    if any(sdrf_dir.iterdir()):
        v_space(2)
        st.markdown("#### SDRF Files in Workspace:")
        df = pd.DataFrame({
            "File Name": [
                f.name for f in sdrf_dir.iterdir()
                if "external_files.txt" not in f.name
            ]
        })
        show_table(df)

        st.markdown("###### 🗑️ Delete SDRF Files:")
        for f in sdrf_dir.iterdir():
            if "external_files.txt" in f.name:
                continue
            col1, col2 = st.columns([4, 1])
            col1.write(f.name)
            if col2.button("🗑️ Delete", key=f"sdrf_del_{f.name}"):
                f.unlink()
                st.rerun()

# FASTA Upload Tab
with sub_tabs[1]:
    st.markdown("#### 🔼 Option 1: Upload FASTA Files Directly")
    with st.form("fasta-upload", clear_on_submit=True):
        files = st.file_uploader(
            "Upload FASTA files", type=["fasta", "fa"],
            accept_multiple_files=(st.session_state.location == "local")
        )
        if st.form_submit_button("Add FASTA files", type="primary"):
            if files:
                fasta_upload.save_uploaded_fasta(files)
            else:
                st.warning("Please select FASTA files.")

    st.markdown("---")

    st.markdown("#### 📁 Option 2: Import FASTA Files from Local Folder")
    if st.session_state.location == "local":
        if st.button("📁 Browse FASTA folder", disabled=not TK_AVAILABLE):
            st.session_state["local_fasta_dir"] = tk_directory_dialog("Select FASTA directory", st.session_state["previous_dir"])
            st.session_state["previous_dir"] = st.session_state["local_fasta_dir"]

        local_fasta_dir = st.text_input("Path to FASTA folder", value=st.session_state.get("local_fasta_dir", ""))
        if st.button("Copy FASTA files", disabled=(local_fasta_dir == "")):
            use_copy = st.checkbox("Copy files", key="fasta_copy", value=True)
            if not use_copy:
                st.warning("Using original files. Ensure paths remain valid.")
            fasta_upload.copy_local_fasta_files_from_directory(local_fasta_dir, use_copy)

    # Show FASTA files in workspace
    if any(fasta_dir.iterdir()):
        v_space(2)
        st.markdown("#### FASTA Files in Workspace:")
        df = pd.DataFrame({
            "File Name": [
                f.name for f in fasta_dir.iterdir()
                if "external_files.txt" not in f.name
            ]
        })
        show_table(df)

        st.markdown("###### 🗑️ Delete FASTA Files:")
        for f in fasta_dir.iterdir():
            if "external_files.txt" in f.name:
                continue
            col1, col2 = st.columns([4, 1])
            col1.write(f.name)
            if col2.button("🗑️ Delete", key=f"fasta_del_{f.name}"):
                f.unlink()
                st.rerun()

# --------- TAB 2: Configure ---------
with tabs[1]:
    st.subheader("Select Nextflow Execution Profile")
    st.session_state.profile = st.selectbox(
        "Execution Profile", ["docker", "singularity", "conda"],
        key="profile_selection"
    )

# --------- TAB 3: Run ---------
with tabs[2]:
    st.subheader("Run Analysis")

    sdrf_files = list(sdrf_dir.glob("*.tsv")) + list(sdrf_dir.glob("*.sdrf"))
    fasta_files = list(fasta_dir.glob("*.fasta")) + list(fasta_dir.glob("*.fa"))

    if not sdrf_files:
        st.warning("Please upload at least one SDRF file in the 'File Upload' tab.")
    if not fasta_files:
        st.warning("Please upload at least one FASTA file in the 'File Upload' tab.")

    if st.button("Start Workflow") and sdrf_files and fasta_files:
        sdrf_path = str(sdrf_files[0])
        fasta_path = str(fasta_files[0])
        profile = st.session_state.get("profile", "docker")

        command_placeholder = st.empty()
        status_placeholder = st.empty()
        output_placeholder = st.empty()
        output_lines = ""
        returncode = None

        for kind, value in CommandExecutor.run_nextflow(sdrf_path, fasta_path, profile):
            if kind == "cmd":
                command_placeholder.code(value, language="bash")
            if kind == "log_update":
                output_lines = value
                output_placeholder.text_area("Analysis Log", output_lines, height=400)
            elif kind == "returncode":
                returncode = value

        if returncode == 0:
            status_placeholder.success("The analysis completed successfully.")

            results_dir = Path("/workspace/results")
            zip_path = results_dir.with_suffix(".zip")
            zip_results_folder(results_dir, zip_path)

            st.session_state["analysis_success"] = True
            st.session_state["results_zip_path"] = str(zip_path)
        else:
            status_placeholder.error(f"An error occurred during the analysis (exit code {returncode}).")
            st.session_state["analysis_success"] = False

# Save state
save_params(params)