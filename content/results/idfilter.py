from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from pyopenms import IdXMLFile
from streamlit_plotly_events import plotly_events

from src.common.common import page_setup

# Page setup
params = page_setup()
st.title("🔍 Peptide Spectrum Matches")
st.info("Here you can explore the PSM scatterplot along with the detailed PSM table.")

# Path to results folder
results_dir = Path(st.session_state.workspace, "results")
idfilter_dir = results_dir / "idfilter"

# Check if path exists
if not idfilter_dir.exists():
    st.warning("❗ 'idfilter' directory not found. Please run the analysis first.")
    st.stop()

# Get list of idXML files
idxml_files = sorted(idfilter_dir.glob("*.idXML"))
if not idxml_files:
    st.info("No idXML files found in the 'idfilter' directory.")
    st.stop()

# Convert idXML → DataFrame
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
        # Convert Charge to categorical string
        df["Charge"] = df["Charge"].astype(str)
        charge_order = sorted(df["Charge"].unique(), key=lambda x: int(x))
        df["Charge"] = pd.Categorical(df["Charge"], categories=charge_order, ordered=True)

        # Add numeric column for color scale
        df["Charge_num"] = df["Charge"].astype(int)

    return df


# Create tabs based on file names
tabs = st.tabs([f.stem.split("_")[0] for f in idxml_files])

for tab, idxml_file in zip(tabs, idxml_files):
    with tab:
        st.markdown(f"### 🧾 {idxml_file.name}")

        try:
            df = idxml_to_dataframe(str(idxml_file))
            if df.empty:
                st.info("No peptide hits found in this file.")
                continue

            # Add index as a column
            df_with_index = df.reset_index()

            # Display the full DataFrame
            st.dataframe(df, use_container_width=True)

            # Prepare data for RT vs m/z scatter plot
            df_with_index['custom_index'] = df_with_index['index'] # Add custom index for plotly events
            
            fig = px.scatter(
                df_with_index,
                x="RT",
                y="m/z",
                color="Score",
                custom_data=['custom_index', 'Sequence', 'Proteins'], # Include additional info for hover
                color_continuous_scale=["#a6cee3", "#1f78b4", "#08519c", "#08306b"]
            )

            # Configure hovertemplate to show index first
            fig.update_traces(
                marker=dict(size=6, opacity=0.8),
                hovertemplate='<b>Index: %{customdata[0]}</b><br>' +
                              'RT: %{x:.2f}<br>' +
                              'm/z: %{y:.4f}<br>' +
                              'Score: %{marker.color:.3f}<br>' +
                              'Sequence: %{customdata[1]}<br>' +
                              'Proteins: %{customdata[2]}<br>' +
                              '<extra></extra>'
            )

            fig.update_layout(
                legend_title_text="Score",
                coloraxis_colorbar=dict(title="Score"),
                hovermode="closest"
            )

            # Enable clickable scatter plot and display
            clicked = plotly_events(
                fig,
                click_event=True,
                hover_event=False,
                override_height=600
            )

            # If a point is clicked, show the corresponding DataFrame row
            if clicked:
                row_index = clicked[0]["pointNumber"]
                st.subheader("📌 Selected Peptide Match")
                st.dataframe(df.iloc[[row_index]], use_container_width=True)

        except Exception as e:
            st.error(f"Failed to load {idxml_file.name}: {e}")