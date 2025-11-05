from pathlib import Path
import streamlit as st
import pandas as pd

from src.common.common import page_setup

# 페이지 설정
params = page_setup()
st.title("📊 Proteomicslfq")

# 결과 폴더 경로
results_dir = Path(st.session_state.workspace, "results")
proteomicslfq_dir = results_dir / "proteomicslfq"

if not proteomicslfq_dir.exists():
    st.warning("❗ 'proteomicslfq' directory not found. Please run the analysis first.")
    st.stop()

csv_files = sorted(proteomicslfq_dir.glob("*.csv"))

if not csv_files:
    st.info("No CSV files found in the 'proteomicslfq' directory.")
    st.stop()

tabs = st.tabs([f.stem for f in csv_files])

for tab, csv_file in zip(tabs, csv_files):
    with tab:
        st.markdown(f"### 🧾 {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                st.info("No data found in this file.")
                continue

            st.dataframe(df, use_container_width=True)
            # Reference 열에서 .mzML 제거
            df['Sample'] = df['Reference'].str.replace('.mzML', '', regex=False)

            # 모든 Sample 열 자동 생성 (중복 제거 후 정렬)
            all_samples = sorted(df['Sample'].unique())

            # Pivot table 생성
            pivot_list = []

            for protein, group in df.groupby('ProteinName'):
                # PeptideSequence 모두 합치기
                peptides = ";".join(group['PeptideSequence'].unique())

                # Sample별 Intensity 합산
                intensity_dict = group.groupby('Sample')['Intensity'].sum().to_dict()

                # 없는 Sample 값은 0으로 채우기
                intensity_dict_complete = {sample: intensity_dict.get(sample, 0) for sample in all_samples}

                # 최종 row 생성
                row = {'ProteinName': protein, **intensity_dict_complete, 'PeptideSequence': peptides}
                pivot_list.append(row)

            pivot_df = pd.DataFrame(pivot_list)

            # 열 순서 지정: ProteinName + all_samples + PeptideSequence
            pivot_df = pivot_df[['ProteinName'] + all_samples + ['PeptideSequence']]

            st.dataframe(pivot_df, use_container_width=True)

        except Exception as e:
            st.error(f"Failed to load {csv_file.name}: {e}")