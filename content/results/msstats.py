from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.common.common import page_setup

# Page setup
params = page_setup()
st.title("📈 MSstats Results")

# Path to results folder
results_dir = Path(st.session_state.workspace, "results")
msstats_dir = results_dir / "msstats"

# Check if path exists
if not msstats_dir.exists():
    st.warning("❗ 'msstats' directory not found. Please run the analysis first.")
    st.stop()

# Get list of CSV files
csv_files = sorted(msstats_dir.glob("*.csv"))

if not csv_files:
    st.info("No CSV files found in the 'msstats' directory.")
    st.stop()

# Use the first (or only) CSV file
csv_file = csv_files[0]
st.markdown(f"### 🧾 {csv_file.name}")

try:
    df = pd.read_csv(csv_file, sep="\t")

    if df.empty:
        st.info("No data found in this file.")
        st.stop()

    st.dataframe(df, use_container_width=True)

    # Volcano plot cutoff settings
    st.markdown("### ⚙️ Volcano Plot Cutoff Settings")

    cols = st.columns(2)
    with cols[0]:
        pvalue_cutoff = st.number_input(
            "adj.pvalue cutoff", min_value=0.0, max_value=1.0, value=0.05, step=0.01
        )
    with cols[1]:
        log2fc_cutoff = st.number_input(
            "log2FC cutoff", min_value=0.0, value=1.0, step=0.1
        )

    # Volcano plot
    if 'log2FC' in df.columns and 'adj.pvalue' in df.columns:
        df['neg_log10_pvalue'] = -np.log10(df['adj.pvalue'].replace(0, np.nan))

        # Assign colors based on cutoff
        df['color'] = np.where(
            (df['log2FC'] > log2fc_cutoff) & (df['adj.pvalue'] < pvalue_cutoff), 'red',
            np.where((df['log2FC'] < -log2fc_cutoff) & (df['adj.pvalue'] < pvalue_cutoff), 'blue', 'grey')
        )

        fig = px.scatter(
            df,
            x='log2FC',
            y='neg_log10_pvalue',
            hover_data=df.columns,
            color='color',
            color_discrete_map={'red': 'red', 'blue': 'blue', 'grey': 'lightgrey'},
            labels={'neg_log10_pvalue': '-log10(adj.pvalue)'}
        )

        # Add cutoff lines
        fig.add_hline(y=-np.log10(pvalue_cutoff), line_dash="dash", line_color="grey",
                      annotation_text=f"p-value cutoff ({pvalue_cutoff})", annotation_position="top left")
        fig.add_vline(x=log2fc_cutoff, line_dash="dash", line_color="grey",
                      annotation_text=f"log2FC cutoff (+{log2fc_cutoff})", annotation_position="top right")
        fig.add_vline(x=-log2fc_cutoff, line_dash="dash", line_color="grey",
                      annotation_text=f"log2FC cutoff (-{log2fc_cutoff})", annotation_position="bottom left")

        fig.update_layout(title="Volcano Plot", xaxis_title="log2 Fold Change", yaxis_title="-log10(adj.pvalue)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Columns 'log2FC' or 'adj.pvalue' not found for volcano plot.")

except Exception as e:
    st.error(f"Failed to load {csv_file.name}: {e}")