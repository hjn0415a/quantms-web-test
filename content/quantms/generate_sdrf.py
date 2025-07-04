import streamlit as st
import pandas as pd
import re
from src.common.common import page_setup

page_setup()

st.title("📃 Generate SDRF file")


with st.form("sdrf_form", clear_on_submit=False):
    cols = st.columns(3)

    with cols[0]:
        source_name = st.text_input("Source Name", placeholder="e.g. PXD040438-Sample-1")
        cell_type = st.text_input("Cell Type", placeholder="e.g. not applicable")
        assay_name = st.text_input("Assay Name", placeholder="e.g. 03COVID")

    with cols[1]:
        organism = st.text_input("Organism", placeholder="e.g. Homo sapiens")
        disease = st.text_input("Disease", placeholder="e.g. COVID-19")
        technology_type = st.text_input("Technology Type", placeholder="e.g. proteomic profiling by mass spectrometry")

    with cols[2]:
        organism_part = st.text_input("Organism Part(Characteristics)", placeholder="e.g. blood plasma")
        bio_replicate = st.selectbox("Biological Replicate", options=["1", "2"], index=0)

    cols = st.columns(2)

    with cols[0]:
        data_file = st.text_input("Data File Name", placeholder="e.g. 03COVID.raw")

    with cols[1]:
        file_uri = st.text_input("File URI", value="https://ftp.pride.ebi.ac.uk/pride/data/archive/2023/03/PXD040438/03COVID.raw")

    cols = st.columns(3)

    with cols[0]:
        fraction_identifier = st.selectbox("Fraction Identifier", options=["1", "2"], index=0)
        technical_replicate = st.selectbox("Technical Replicate", options=["1", "2"], index=0)

        # instrument_ac = st.selectbox("Instrument (AC)", options=["MS:1000073"])
        # instrument_nt = st.selectbox("Instrument (NT)", options=["Electrospray ionization"])
        # instrument = f"AC={instrument_ac}; NT={instrument_nt}"

        instrument = st.text_input("Instrument", placeholder="e.g. AC=MS:1000073; NT=Electrospray ionization")
        modification_2 = st.text_input("Modification Parameter 2", placeholder="e.g. NT=Met-loss;AC=UNIMOD:765;MT=Variable;TA=M")
        dissociation_method = st.text_input("Dissociation Method", placeholder="e.g. AC=MS:1000422;NT=HCD")
        fragment_mass_tolerance_val = st.number_input("Fragment Mass Tolerance(Da)", value=0.6, step=0.1, format="%.1f")
        fragment_mass_tolerance = f"{fragment_mass_tolerance_val} Da"

    with cols[1]:
        fractionation_method = st.text_input("Fractionation Method", placeholder="e.g. no fractionation")
        cleavage_agent = st.text_input("Cleavage Agent Details", placeholder="e.g. NT=Trypsin; AC=MS:1001251")
        separation = st.text_input("Separation", placeholder="e.g. AC=PRIDE:0000563;NT=Reversed-phase chromatography")
        modification_3 = st.text_input("Modification Parameter 3", placeholder="e.g. NT =Met-loss+Acetyl;AC=UNIMOD:766;MT=Variable;TA=M")
        collision_energy_val = st.number_input("Collision Energy(NCE)", value=30, step=1)
        collision_energy = f"{collision_energy_val} NCE"
        factor_organism_part = st.text_input("Organism Part(Factor Value)", placeholder="e.g. blood plasma")

    with cols[2]:
        label = st.text_input("Label", placeholder="e.g. AC=MS:1002038;NT=label free sample")
        mass_analyzer = st.text_input("MS2 Mass Analyzer", placeholder="e.g. AC=MS:1003029; NT=Orbitrap Eclipse")
        modification_1 = st.text_input("Modification Parameter 1", placeholder="e.g. NT=Carbamidomethyl;AC=UNIMOD:4;TA=C;MT=Variable")
        modification_4 = st.text_input("Modification Parameter 4", placeholder="e.g. NT=Oxidation;AC=UNIMOD:35;MT=Variable;TA=M")
        precursor_mass_tolerance_val = st.number_input("Precursor Mass Tolerance(ppm)", value=20, step=1)
        precursor_mass_tolerance = f"{precursor_mass_tolerance_val} ppm"


    submitted = st.form_submit_button("Generate SDRF File")

if submitted:
    match = re.match(r"^([^-]+)", source_name)
    if not match:
        st.error("Invalid Source Name format. Expected format like 'PXD040438-Sample-1'")
    else:
        project_id = match.group(1)
        file_name = f"{project_id}.sdrf.tsv"

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
            "comment[modification parameter]": modification_1,
            "comment[modification parameter]": modification_2,
            "comment[modification parameter]": modification_3,
            "comment[modification parameter]": modification_4,
            "comment[dissociation method]": dissociation_method,
            "comment[collision energy]": collision_energy,
            "comment[precursor mass tolerance]": precursor_mass_tolerance,
            "comment[fragment mass tolerance]": fragment_mass_tolerance,
            "factor value[organism part]": factor_organism_part
        }

        df = pd.DataFrame([sdrf_row])

        df.to_csv(file_name, sep='\t', index=False)
        st.success(f"✅ SDRF file generated: `{file_name}`")
        st.download_button("Download SDRF File", df.to_csv(sep="\t", index=False), file_name=file_name, mime="text/tab-separated-values")