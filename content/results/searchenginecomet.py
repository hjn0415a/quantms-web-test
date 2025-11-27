from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from pyopenms import IdXMLFile

from src.common.common import page_setup

# Page setup
params = page_setup()
st.title("🔎 Searchenginecomet")

# Path to results folder
results_dir = Path(st.session_state.workspace, "results")
searchenginecomet_dir = results_dir / "searchenginecomet"

# Check directory existence
if not searchenginecomet_dir.exists():
    st.warning("❗ 'searchenginecomet' directory not found. Please run the analysis first.")
    st.stop()

# Get list of idXML files
idxml_files = sorted(searchenginecomet_dir.glob("*.idXML"))

if not idxml_files:
    st.info("No idXML files found in the 'searchenginecomet' directory.")
    st.stop()

# Convert idXML -> DataFrame
def idxml_to_dataframe(idxml_file: str) -> pd.DataFrame:
    proteins = []
    peptides = []
    IdXMLFile().load(str(idxml_file), proteins, peptides)

    records = []
    for pep in peptides:
        rt = pep.getRT()
        mz = pep.getMZ()
        for hit in pep.getHits():
            protein_refs = [ev.getProteinAccession() for ev in hit.getPeptideEvidences()]
            records.append({
                "RT": rt,
                "m/z": mz,
                "Sequence": hit.getSequence().toString(),
                "Charge": hit.getCharge(),
                "Score": hit.getScore(),
                "Proteins": ",".join(protein_refs) if protein_refs else None
            })
    df = pd.DataFrame(records)
    if not df.empty:
        # Convert Charge to ordered categorical type
        df["Charge"] = df["Charge"].astype(str)
        charge_order = sorted(df["Charge"].unique())
        df["Charge"] = pd.Categorical(df["Charge"], categories=charge_order, ordered=True)

        # Add numeric column for color scaling (optional)
        df["Charge_num"] = df["Charge"].astype(int)

    return df

# Create a tab for each file
tabs = st.tabs([f.stem.split("_")[0] for f in idxml_files])

for tab, idxml_file in zip(tabs, idxml_files):
    with tab:
        st.markdown(f"### 🧾 {idxml_file.name}")

        try:
            df = idxml_to_dataframe(str(idxml_file))
            
            if df.empty:
                st.info("No peptide hits found in this file.")
                continue

            # RT vs m/z scatter plot
            fig = px.scatter(
                df,
                x="RT",
                y="m/z",
                color="Charge",
                hover_data=["Sequence", "Score", "Proteins"],
                category_orders={"Charge": df["Charge"].cat.categories},
                color_discrete_sequence=["#a6cee3", "#1f78b4", "#08519c", "#08306b"]  # Gradient blue tone
            )
            fig.update_traces(marker=dict(size=4, opacity=0.7))  # Adjust marker size and tansparency
            fig.update_layout(coloraxis_colorbar=dict(title="Charge"))

            st.plotly_chart(fig, use_container_width=True)

            # Display DataFrame
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Failed to load {idxml_file.name}: {e}")