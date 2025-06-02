import shutil
from pathlib import Path

import streamlit as st

from src.common.common import reset_directory

def save_uploaded_sdrf(uploaded_files: list[bytes]) -> None:
    """
    Saves uploaded SDRF files to the sdrf directory.
    """
    sdrf_dir = Path(st.session_state.workspace, "sdrf-files")

    if st.session_state.location == "online":
        uploaded_files = [uploaded_files]

    if not uploaded_files:
        st.warning("Upload some SDRF files first.")
        return

    for f in uploaded_files:
        if f.name not in [f.name for f in sdrf_dir.iterdir()] and f.name.endswith((".sdrf", ".tsv")):
            with open(Path(sdrf_dir, f.name), "wb") as fh:
                fh.write(f.getbuffer())
    st.success("Successfully added uploaded SDRF files!")

def copy_local_sdrf_files_from_directory(local_sdrf_directory: str, make_copy: bool = True) -> None:
    """
    Copies local SDRF files from a specified directory to the sdrf directory.
    """
    sdrf_dir = Path(st.session_state.workspace, "sdrf-files")
    valid_exts = (".sdrf", ".tsv")

    files = [f for f in Path(local_sdrf_directory).iterdir() if f.suffix.lower() in valid_exts]

    if not files:
        st.warning("No SDRF files found in specified folder.")
        return

    for f in files:
        if make_copy:
            shutil.copy(f, Path(sdrf_dir, f.name))
        else:
            external_files = Path(sdrf_dir, "external_files.txt")
            if not external_files.exists():
                external_files.touch()
            with open(external_files, "a") as f_handle:
                f_handle.write(f"{f}\n")

    st.success("Successfully added local SDRF files!")

def remove_selected_sdrf_files(to_remove: list[str], params: dict) -> dict:
    """
    Removes selected SDRF files from the sdrf directory.
    """
    sdrf_dir = Path(st.session_state.workspace, "sdrf-files")

    for f in to_remove:
        Path(sdrf_dir, f).unlink(missing_ok=True)

    for k, v in params.items():
        if isinstance(v, list) and any(f in v for f in to_remove):
            params[k] = [item for item in v if item not in to_remove]

    st.success("Selected SDRF files removed!")
    return params

def remove_all_sdrf_files(params: dict) -> dict:
    """
    Removes all SDRF files from the sdrf directory.
    """
    from src.common.common import reset_directory

    sdrf_dir = Path(st.session_state.workspace, "sdrf-files")
    reset_directory(sdrf_dir)

    for k, v in params.items():
        if "sdrf" in k and isinstance(v, list):
            params[k] = []

    st.success("All SDRF files removed!")
    return params