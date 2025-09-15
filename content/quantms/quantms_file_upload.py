from pathlib import Path
import streamlit as st
import pandas as pd
import zipfile
import json

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

def load_default_values():
    BASE_DIR = Path(__file__).parent
    ROOT_DIR = BASE_DIR.parent.parent
    json_path = ROOT_DIR / "default-values.json"

    if not json_path.exists():
        st.error(f"default-values.json not found at {json_path}")
        return {}
    
    with open(json_path, "r") as f:
        return json.load(f)

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
    st.markdown("#### 🔼 Upload SDRF Files Directly")
    with st.form("sdrf-upload", clear_on_submit=True):
        files = st.file_uploader(
            "Upload SDRF", type=["sdrf", "tsv"],
            accept_multiple_files=(st.session_state.location == "local")
        )
        if st.form_submit_button("Add SDRF files", type="primary"):
            if files:
                sdrf_upload.save_uploaded_sdrf(files)
            else:
                st.warning("Please select SDRF files.")

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
    st.markdown("#### Upload FASTA Files Directly")
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
    st.selectbox(
        "Execution Profile", ["docker", "singularity", "conda"],
        key="profile"
    )

    st.subheader("Tools flags")

    col1, col2, col3 = st.columns(3)

    # Boolean options
    with col1:
        st.selectbox("Add Decoys", [False, True], key="add_decoys")
    with col2:
        st.selectbox("Skip Rescoring", [False, True], key="skip_rescoring")
    with col3:
        st.selectbox("PSM Clean", [False, True], key="psm_clean")

    # Text option
    st.selectbox("Search Engines", ["comet", "msfragger", "other"], key="search_engines")

    # Numeric options
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Sage Processes", min_value=1, step=1, value=1, key="sage_processes")
    with col2:
        st.number_input("Run FDR Cutoff", min_value=0.0, max_value=1.0, step=0.01,
                        value=0.10, format="%.2f", key="run_fdr_cutoff")
    with col3:
        st.number_input("Protein-level FDR Cutoff", min_value=0.0, max_value=1.0, step=0.01,
                        value=0.01, format="%.2f", key="protein_level_fdr_cutoff")

    # PSM-level FDR Cutoff
    st.number_input("PSM-level FDR Cutoff", min_value=0.0, max_value=1.0, step=0.01,
                    value=0.01, format="%.2f", key="psm_level_fdr_cutoff")
    
    with st.expander("**Advanced parameters** (Debug Level)"):

        st.subheader("Debug Level")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.selectbox("decoydatabase_debug", [0, 1, 2], key="decoydatabase_debug")
            st.selectbox("pp_debug", [0, 1, 2], key="pp_debug")
            st.selectbox("extractpsmfeature_debug", [0, 1, 2], key="extractpsmfeature_debug")
            st.selectbox("idfilter_debug", [0, 1, 2], key="idfilter_debug")
            st.selectbox("idscoreswitcher_debug", [0, 1, 2], key="idscoreswitcher_debug")

        with col2:
            st.selectbox("iso_debug", [0, 1, 2], key="iso_debug")
            st.selectbox("db_debug", [0, 1, 2], key="db_debug")
            st.selectbox("percolator_debug", [0, 1, 2], key="percolator_debug")
            st.selectbox("consensusid_debug", [0, 1, 2], key="consensusid_debug")
            st.selectbox("idmapper_debug", [0, 1, 2], key="idmapper_debug")

        with col3:
            st.selectbox("luciphor_debug", [0, 1, 2], key="luciphor_debug")
            st.selectbox("protein_inference_debug", [0, 1, 2], key="protein_inference_debug")
            st.selectbox("plfq_debug", [0, 1, 2], key="plfq_debug")
            st.selectbox("protein_quant_debug", [0, 1, 2], key="protein_quant_debug")

    with st.expander("**Advanced parameters** (Decoy Settings)"):

        st.subheader("Decoy Settings")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.selectbox("decoy_string", ["DECOY_"], key="decoy_string")
            st.selectbox("decoy_string_position", ["prefix"], key="decoy_string_position")

        with col2:
            st.selectbox("decoy_method", ["reverse"], key="decoy_method")
            st.number_input("shuffle_max_attempts", min_value=1, step=1, value=30, key="shuffle_max_attempts")

        with col3:
            st.number_input("shuffle_sequence_identity_threshold", min_value=0.0, max_value=1.0,
                            step=0.01, value=0.5, format="%.2f", key="shuffle_sequence_identity_threshold")

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
        workdir = st.session_state.workspace

        command_placeholder = st.empty()
        status_placeholder = st.empty()
        log_placeholder = st.empty()
        output_lines = []
        returncode = None

        default_values = load_default_values()

        changed_values = {
            k: v for k, v in st.session_state.items()
            if k in default_values and default_values[k] != v
        }

        config_args = ' '.join(f'--{k} {v}' for k, v in changed_values.items())
        config_args += " --skip_post_msstats True"
        st.write(config_args)
        

        for kind, value in CommandExecutor.run_nextflow(sdrf_path, fasta_path, workdir, config_args, profile):
            if kind == "debug":
                st.code(value, language="bash")
            elif kind == "cmd":
                command_placeholder.code(value, language="bash")
            elif kind == "log_update":
                output_lines.append(value)
                log_placeholder.text_area("Analysis Log", "\n".join(output_lines), height=400)
            elif kind == "returncode":
                returncode = value

        if returncode == 0:
            status_placeholder.success("The analysis completed successfully.")

            results_dir = Path(st.session_state.workspace, "results")

            zip_path = results_dir.with_suffix(".zip")
            zip_results_folder(results_dir, zip_path)

            st.session_state["analysis_success"] = True
        else:
            status_placeholder.error(f"An error occurred during the analysis (exit code {returncode}).")
            st.session_state["analysis_success"] = False

# Save state
save_params(params)
