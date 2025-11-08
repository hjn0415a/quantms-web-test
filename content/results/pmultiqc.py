from pathlib import Path
import streamlit as st
from src.common.common import page_setup

# 페이지 설정
params = page_setup()

# 제목 (subheader 크기로, 중앙 정렬 + 간격 추가)
st.markdown(
    """
    <h2 style='font-weight:700; margin-bottom:40px;'>
        📊 MultiQC Plots Summary
    </h2>
    """,
    unsafe_allow_html=True
)

results_dir = Path(st.session_state.workspace, "results")
png_dir = results_dir / "summarypipeline" / "multiqc_plots" / "png"

# 상단 2열로 출력할 파일 (Heatmap + ms1_tic)
overview_files = {
    "HeatMap.png" : 'Performance Overview',
    "ms1_tic.png" : 'Total Ion Chromatogram'
}

# 하단 2열로 출력할 파일 (상세 분포)
detailed_files = {
    "peak_intensity_distribution-cnt.png" : 'Peak Intensity Distribution (Absolute)',
    "peak_intensity_distribution-pct.png" : 'Peak Intensity Distribution (Relative)',
    "peaks_per_ms2-cnt.png" : 'Number of Peaks (Absolute)',
    "peaks_per_ms2-pct.png" : 'Number of Peaks (Relative)',
}

# --- Overview section ---
overview_cols = st.columns(2)
for i, (png_file, display_name) in enumerate(overview_files.items()):
    img_path = png_dir / png_file
    if img_path.exists():
        with overview_cols[i % 2]:
            st.markdown(
                f"<h5 style='text-align:center; font-weight:700; font-size:22px;'>{display_name}</h5>",
                unsafe_allow_html=True
            )
            st.image(str(img_path), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        overview_cols[i % 2].warning(f"{png_file} not found.")

st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

# --- Detailed section ---
detailed_cols = st.columns(2)
for i, (png_file, display_name) in enumerate(detailed_files.items()):
    img_path = png_dir / png_file
    if img_path.exists():
        with detailed_cols[i % 2]:
            st.markdown(
                f"<h5 style='text-align:center; font-weight:700; font-size:20px;'>{display_name}</h5>",
                unsafe_allow_html=True
            )
            st.image(str(img_path), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        detailed_cols[i % 2].warning(f"{png_file} not found.")