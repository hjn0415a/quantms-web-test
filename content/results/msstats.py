from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

from src.common.common import page_setup

# Page setup
params = page_setup()
st.title("📈 Statistical Analysis")

# Path to results folder
results_dir = Path(st.session_state.workspace, "results")
msstats_dir = results_dir / "msstats"

if not msstats_dir.exists():
    st.warning("❗ 'msstats' directory not found. Please run the analysis first.")
    st.stop()

# Get list of CSV files
csv_files = sorted(msstats_dir.glob("*.csv"))
if not csv_files:
    st.info("No CSV files found in the 'msstats' directory.")
    st.stop()

# Use the first (or only) detected CSV file
csv_file = csv_files[0]
st.markdown(f"### 🧾 {csv_file.name}")

try:
    df = pd.read_csv(csv_file, sep="\t")
    
    if df.empty:
        st.info("No data found in this file.")
        st.stop()

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

    # Show full table first
    st.dataframe(df, use_container_width=True)

    # Volcano plot generation
    if 'log2FC' in df.columns and 'adj.pvalue' in df.columns:
        # Create dataframe for plotting while preserving original row index
        df_plot = df.copy().reset_index()
        df_plot['neg_log10_pvalue'] = -np.log10(df_plot['adj.pvalue'].replace(0, np.nan))

        # Assign group labels based on cutoff rules
        df_plot['color'] = np.where(
            (df_plot['log2FC'] > log2fc_cutoff) & (df_plot['adj.pvalue'] < pvalue_cutoff), 'Up-regulated',
            np.where((df_plot['log2FC'] < -log2fc_cutoff) & (df_plot['adj.pvalue'] < pvalue_cutoff), 'Down-regulated', 'Not significant')
        )

        # Remove invalid values
        df_plot_clean = df_plot.dropna(subset=['neg_log10_pvalue', 'log2FC']).copy()
        
        # Create Plotly scatter plot (group-wise)
        fig = go.Figure()
        
        colors = {
            'Up-regulated': 'red',
            'Down-regulated': 'blue',
            'Not significant': 'lightgrey'
        }
        
        for group_name, color in colors.items():
            group_data = df_plot_clean[df_plot_clean['color'] == group_name]
            
            if len(group_data) > 0:
                # Build hover text containing full original row metadata
                hover_texts = []
                for idx, row in group_data.iterrows():
                    original_idx = int(row['index'])
                    original_row = df.iloc[original_idx]
                    
                    text_parts = [f"<b>Index: {original_idx}</b>"]
                    for col in df.columns:
                        text_parts.append(f"{col}: {original_row[col]}")
                    text_parts.append(f"<br>-log10(pvalue): {row['neg_log10_pvalue']:.3f}")
                    
                    hover_texts.append("<br>".join(text_parts))
                
                fig.add_trace(go.Scatter(
                    x=group_data['log2FC'],
                    y=group_data['neg_log10_pvalue'],
                    mode='markers',
                    name=group_name,
                    marker=dict(color=color, size=6, opacity=0.8),
                    customdata=group_data['index'].values.reshape(-1, 1),
                    hovertext=hover_texts,
                    hoverinfo='text'
                ))

        # Add threshold reference lines
        fig.add_hline(y=-np.log10(pvalue_cutoff), line_dash="dash", line_color="grey",
                      annotation_text=f"p-value cutoff ({pvalue_cutoff})", annotation_position="top left")
        fig.add_vline(x=log2fc_cutoff, line_dash="dash", line_color="grey",
                      annotation_text=f"log2FC cutoff (+{log2fc_cutoff})", annotation_position="top right")
        fig.add_vline(x=-log2fc_cutoff, line_dash="dash", line_color="grey",
                      annotation_text=f"log2FC cutoff (-{log2fc_cutoff})", annotation_position="bottom left")

        fig.update_layout(
            title="Volcano Plot",
            xaxis_title="log2 Fold Change",
            yaxis_title="-log10(adj.pvalue)",
            hovermode="closest",
            showlegend=True
        )

        # Display interactive Plotly chart
        clicked = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            override_height=600,
        )

        # Show selected row if a point was clicked
        if clicked:
            # Extract original row index from customdata or fallback
            if 'customdata' in clicked[0] and clicked[0]['customdata']:
                original_index = int(clicked[0]['customdata'][0])
            else:
                # Fallback: use pointNumber + curveNumber
                curve_number = clicked[0].get('curveNumber', 0)
                point_number = clicked[0]['pointNumber']
            
                trace_data = fig.data[curve_number]
                original_index = int(trace_data.customdata[point_number][0])
            
            st.subheader("📌 Selected Data Point")
            st.dataframe(df.iloc[[original_index]], use_container_width=True)

    else:
        st.info("Columns 'log2FC' or 'adj.pvalue' not found for volcano plot.")

except Exception as e:
    st.error(f"Failed to load {csv_file.name}: {e}")