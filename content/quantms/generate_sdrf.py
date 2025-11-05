import streamlit as st
import pandas as pd
import re
from src.common.common import page_setup

page_setup()

st.title("📃 Generate SDRF file")
st.info("💡 This section is for generating an SDRF file if you don't already have one.\n\nIf you already have an SDRF file, please proceed directly to the **Workflow** tab.")
# Initialize session state
if "sdrf_rows" not in st.session_state:
    st.session_state["sdrf_rows"] = []

if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

if "success_message" not in st.session_state:
    st.session_state["success_message"] = None

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False

if "delete_mode" not in st.session_state:
    st.session_state["delete_mode"] = False

# Add Row button (disappears after submission)
if not st.session_state["sdrf_rows"]:
    st.session_state["show_form"] = True
    st.session_state["edit_mode"] = False
    st.session_state["delete_mode"] = False
    st.session_state["success_message"] = None

# Display the SDRF table
if st.session_state["sdrf_rows"]:
    st.markdown("---")
    st.markdown("### 📋 Current SDRF Table")

    # Arrange four buttons in a single row
    col_left, col_center, col_right = st.columns([1.5, 1, 1])

    with col_left:
        btn_cols = st.columns(4)
        with btn_cols[0]:
            if st.button("➕ Add Row", use_container_width=True):
                st.session_state["show_form"] = not st.session_state["show_form"]
                st.session_state["edit_mode"] = False
                st.session_state["delete_mode"] = False
                st.session_state["success_message"] = None

        with btn_cols[1]:
            df = pd.DataFrame(st.session_state["sdrf_rows"])
            sample_row = st.session_state["sdrf_rows"][0]
            project_id_match = re.match(r"^([^-]+)", sample_row["source name"])
            project_id = project_id_match.group(1) if project_id_match else "project"
            file_name = f"{project_id}.sdrf.tsv"
            st.download_button(
                "⬇️ Download",
                df.to_csv(sep="\t", index=False),
                file_name=file_name,
                mime="text/tab-separated-values",
                use_container_width=True
            )

        with btn_cols[2]:
            if st.button("✏️ Edit Row", use_container_width=True):
                st.session_state["edit_mode"] = not st.session_state["edit_mode"]
                st.session_state["delete_mode"] = False
                st.session_state["show_form"] = False

        with btn_cols[3]:
            if st.button("🗑️ Delete Row", use_container_width=True):
                st.session_state["delete_mode"] = not st.session_state["delete_mode"]
                st.session_state["edit_mode"] = False
                st.session_state["show_form"] = False

    # Show the SDRF table (only when not in edit/delete mode)
    if not st.session_state["edit_mode"] and not st.session_state["delete_mode"]:
        st.dataframe(df, use_container_width=True)

# ✏️ Edit Mode
if st.session_state.get("edit_mode"):
    st.markdown("### ✏️ Edit Rows")
    edited_df = st.data_editor(
        pd.DataFrame(st.session_state["sdrf_rows"]),
        num_rows="dynamic",
        use_container_width=True,
        key="sdrf_editor"
    )
    if st.button("💾 Save Edits"):
        st.session_state["sdrf_rows"] = edited_df.to_dict(orient="records")
        st.success("✅ Edits saved.")
        st.session_state["edit_mode"] = False
        st.rerun()

# 🗑️ Delete Mode
if st.session_state.get("delete_mode"):
    st.markdown("### 🗑️ Delete a Row")
    df_for_delete = pd.DataFrame(st.session_state["sdrf_rows"])
    if not df_for_delete.empty:
        delete_options = [f"{i + 1}: {row['source name']}" for i, row in df_for_delete.iterrows()]
        selected = st.selectbox("Select row to delete", delete_options, index=0)
        if st.button("🗑️ Delete Selected Row"):
            idx_to_delete = int(selected.split(":")[0]) - 1
            st.session_state["sdrf_rows"].pop(idx_to_delete)
            st.success("✅ Row deleted.")
            st.session_state["delete_mode"] = False
            st.rerun()

# 🔽 input form
if st.session_state["show_form"]:
    with st.form("sdrf_form", clear_on_submit=False):
        cols = st.columns(3)
        with cols[0]:
            source_name = st.text_input("Source Name", placeholder="e.g. PXD040438-Sample-1", value="PXD040438-Sample-1")
            cell_type = st.text_input("Cell Type", placeholder="e.g. not applicable", value=st.session_state.get("default_cell_type", "not applicable"))
            assay_name = st.text_input("Assay Name", placeholder="e.g. 03COVID", value=st.session_state.get("default_assay_name", "03COVID"))
        with cols[1]:
            organism = st.text_input("Organism", placeholder="e.g. Homo sapiens", value="Homo sapiens")
            disease = st.text_input("Disease", placeholder="e.g. COVID-19", value="COVID-19")
            technology_type = st.text_input("Technology Type", placeholder="e.g. proteomic profiling by mass spectrometry", value="proteomic profiling by mass spectrometry")
        with cols[2]:
            organism_part = st.text_input("Organism Part(Characteristics)", placeholder="e.g. blood plasma", value="blood plasma")
            bio_replicate = st.selectbox("Biological Replicate", options=["1", "2"], index=0)

        cols = st.columns(2)
        with cols[0]:
            data_file = st.text_input("Data File Name", placeholder="e.g. 03COVID.raw", value="03COVID.raw")
        with cols[1]:
            file_uri = st.text_input("File URI", value="https://ftp.pride.ebi.ac.uk/pride/data/archive/2023/03/PXD040438/03COVID.raw")

        cols = st.columns(3)
        with cols[0]:
            fraction_identifier = st.selectbox("Fraction Identifier", options=["1", "2"], index=0)
            technical_replicate = st.selectbox("Technical Replicate", options=["1", "2"], index=0)
            instrument = st.text_input("Instrument", placeholder="e.g. AC=MS:1000073; NT=Electrospray ionization", value="AC=MS:1000073; NT=Electrospray ionization")
            modification_2 = st.text_input("Modification Parameter 2", placeholder="e.g. NT=Met-loss;AC=UNIMOD:765;MT=Variable;TA=M", value="NT=Met-loss;AC=UNIMOD:765;MT=Variable;TA=M")
            dissociation_method = st.text_input("Dissociation Method", placeholder="e.g. AC=MS:1000422;NT=HCD", value="AC=MS:1000422;NT=HCD")
            fragment_mass_tolerance_val = st.number_input("Fragment Mass Tolerance(Da)", value=0.6, step=0.1, format="%.1f")
            fragment_mass_tolerance = f"{fragment_mass_tolerance_val} Da"

        with cols[1]:
            fractionation_method = st.text_input("Fractionation Method", placeholder="e.g. no fractionation", value="no fractionation")
            cleavage_agent = st.text_input("Cleavage Agent Details", placeholder="e.g. NT=Trypsin; AC=MS:1001251", value="NT=Trypsin; AC=MS:1001251")
            separation = st.text_input("Separation", placeholder="e.g. AC=PRIDE:0000563;NT=Reversed-phase chromatography", value="AC=PRIDE:0000563;NT=Reversed-phase chromatography")
            modification_3 = st.text_input("Modification Parameter 3", placeholder="e.g. NT=Met-loss+Acetyl;AC=UNIMOD:766;MT=Variable;TA=M", value="NT=Met-loss+Acetyl;AC=UNIMOD:766;MT=Variable;TA=M")
            collision_energy_val = st.number_input("Collision Energy(NCE)", value=30, step=1)
            collision_energy = f"{collision_energy_val} NCE"
            factor_organism_part = st.text_input("Organism Part(Factor Value)", placeholder="e.g. blood plasma", value="blood plasma")

        with cols[2]:
            label = st.text_input("Label", placeholder="e.g. AC=MS:1002038;NT=label free sample", value="AC=MS:1002038;NT=label free sample")
            mass_analyzer = st.text_input("MS2 Mass Analyzer", placeholder="e.g. AC=MS:1003029; NT=Orbitrap Eclipse", value="AC=MS:1003029; NT=Orbitrap Eclipse")
            modification_1 = st.text_input("Modification Parameter 1", placeholder="e.g. NT=Carbamidomethyl;AC=UNIMOD:4;TA=C;MT=Variable", value="NT=Carbamidomethyl;AC=UNIMOD:4;TA=C;MT=Variable")
            modification_4 = st.text_input("Modification Parameter 4", placeholder="e.g. NT=Oxidation;AC=UNIMOD:35;MT=Variable;TA=M", value="NT=Oxidation;AC=UNIMOD:35;MT=Variable;TA=M")
            precursor_mass_tolerance_val = st.number_input("Precursor Mass Tolerance(ppm)", value=20, step=1)
            precursor_mass_tolerance = f"{precursor_mass_tolerance_val} ppm"

        submitted = st.form_submit_button("✅ Submit Row")

    if submitted:
        match = re.match(r"^([^-]+)", source_name)
        if not match:
            st.error("Invalid Source Name format. Expected format like 'PXD040438-Sample-1'")
        else:
            sdrf_row = {
                "source name": source_name,
                "characteristics[organism]": organism,
                "characteristics[organism part]": organism_part,
                "characteristics[cell type]": cell_type,
                "characteristics[disease]": disease,
                "characteristics[biological replicate]": bio_replicate,
                "assay name": assay_name,
                "Technology type": technology_type,
                "comment[data file]": data_file,
                "comment[file uri]": file_uri,
                "comment[fraction identifier]": fraction_identifier,
                "comment[fractionation method]": fractionation_method,
                "comment[label]": label,
                "comment[technical replicate]": technical_replicate,
                "comment[cleavage agent details]": cleavage_agent,
                "comment[MS2 mass analyzer]": mass_analyzer,
                "comment[instrument]": instrument,
                "comment[separation]": separation,
                "comment[modification parameter 1]": modification_1,
                "comment[modification parameter 2]": modification_2,
                "comment[modification parameter 3]": modification_3,
                "comment[modification parameter 4]": modification_4,
                "comment[dissociation method]": dissociation_method,
                "comment[collision energy]": collision_energy,
                "comment[precursor mass tolerance]": precursor_mass_tolerance,
                "comment[fragment mass tolerance]": fragment_mass_tolerance,
                "factor value[organism part]": factor_organism_part
            }
            st.session_state["sdrf_rows"].append(sdrf_row)
            st.session_state["success_message"] = "✅ Row added."
            st.session_state["default_cell_type"] = cell_type
            st.session_state["default_assay_name"] = assay_name
            st.session_state["show_form"] = False
            st.rerun()

if st.session_state.get("success_message"):
    st.success(st.session_state["success_message"])
    st.session_state["success_message"] = None