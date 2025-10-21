from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from pyopenms import IdXMLFile

from src.common.common import page_setup

# 페이지 설정
params = page_setup()
st.title("🧩 ID Filter Results")

# 결과 폴더 경로
results_dir = Path(st.session_state.workspace, "results")
idfilter_dir = results_dir / "idfilter"

# 경로 확인
if not idfilter_dir.exists():
    st.warning("❗ 'idfilter' directory not found. Please run the analysis first.")
    st.stop()

# idXML 파일 리스트 가져오기
idxml_files = sorted(idfilter_dir.glob("*.idXML"))

if not idxml_files:
    st.info("No idXML files found in the 'idfilter' directory.")
    st.stop()

# idXML -> DataFrame 변환 함수
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
        # Charge를 문자열로 변환 후 범주형 지정
        df["Charge"] = df["Charge"].astype(str)
        charge_order = sorted(df["Charge"].unique())
        df["Charge"] = pd.Categorical(df["Charge"], categories=charge_order, ordered=True)
    return df

# 파일 이름으로 탭 생성
tabs = st.tabs([f.stem for f in idxml_files])

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
                title=f"Peptide Identifications (RT vs m/z) - {idxml_file.stem}",
                category_orders={"Charge": df["Charge"].cat.categories},
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig.update_traces(marker=dict(size=8, opacity=0.7))
            st.plotly_chart(fig, use_container_width=True)

            # DataFrame 테이블 표시
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Failed to load {idxml_file.name}: {e}")