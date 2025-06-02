import shutil
from pathlib import Path

import streamlit as st

from src.common.common import reset_directory

def save_uploaded_fasta(uploaded_files: list[bytes]) -> None:
    """
    Saves uploaded FASTA files to the fasta directory.
    """
    fasta_dir = Path(st.session_state.workspace, "fasta-files")

    if st.session_state.location == "online":
        uploaded_files = [uploaded_files]

    if not uploaded_files:
        st.warning("Upload some FASTA files first.")
        return

    for f in uploaded_files:
        if f.name not in [f.name for f in fasta_dir.iterdir()] and f.name.endswith((".fasta", ".fa")):
            with open(Path(fasta_dir, f.name), "wb") as fh:
                fh.write(f.getbuffer())
    st.success("Successfully added uploaded FASTA files!")

def copy_local_fasta_files_from_directory(local_fasta_directory: str, make_copy: bool = True) -> None:
    """
    Copies local FASTA files from a specified directory to the fasta directory.
    Supports .fasta, .fa extensions.
    """
    fasta_dir = Path(st.session_state.workspace, "fasta-files")
    valid_exts = (".fasta", ".fa")

    # file filtering
    files = [f for f in Path(local_fasta_directory).iterdir() if f.suffix.lower() in valid_exts]

    if not files:
        st.warning("No FASTA files found in specified folder.")
        return

    for f in files:
        if make_copy:
            shutil.copy(f, Path(fasta_dir, f.name))
        else:
            external_files = Path(fasta_dir, "external_files.txt")
            if not external_files.exists():
                external_files.touch()
            with open(external_files, "a") as f_handle:
                f_handle.write(f"{f}\n")

    st.success("Successfully added local FASTA files!")

def remove_selected_fasta_files(to_remove: list[str], params: dict) -> dict:
    """
    Removes selected FASTA files from the fasta directory.
    """
    fasta_dir = Path(st.session_state.workspace, "fasta-files")

    for f in to_remove:
        Path(fasta_dir, f).unlink(missing_ok=True)

    for k, v in params.items():
        if isinstance(v, list) and any(f in v for f in to_remove):
            params[k] = [item for item in v if item not in to_remove]

    st.success("Selected FASTA files removed!")
    return params

def remove_all_fasta_files(params: dict) -> dict:
    """
    Removes all FASTA files from the fasta directory.
    """
    from src.common.common import reset_directory

    fasta_dir = Path(st.session_state.workspace, "fasta-files")
    reset_directory(fasta_dir)

    for k, v in params.items():
        if "fasta" in k and isinstance(v, list):
            params[k] = []

    st.success("All FASTA files removed!")
    return params