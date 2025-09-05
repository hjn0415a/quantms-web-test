from pathlib import Path
import streamlit as st

from src.common.common import page_setup

page_setup(page="main")

st.markdown(
        """
        # QuantMS App
        ### QuantMS: A bioinformatics best-practice analysis pipeline for Quantitative Mass Spectrometry
        Welcome to the OpenMS QuantMS App, a web application for the QuantMS quantitative proteomics analysis pipeline built using [OpenMS](https://openms.de/) and Nextflow.
        """
    )

st.markdown("""
      ## Quickstart 

      You can start right away analyzing your data by following the steps below:

      ### 1. Create a workspace
      On the left side of this page a workspace  defined where all your data including uploaded files will be stored. In the web app, you can share your results via the unique workspace ID. Be careful with sensitive data, anyone with access to this ID can view your data.

      ⚠️ Note: In the web app, all users with a unique workspace ID have the same rights.
            
      ### 2. 📁 Upload your files
      Upload `sdrf` and `fasta` files via the **File Upload** tab. The data will be stored in your workspace. With the web app you can upload only one file at a time.
      Locally there is no limit in files. However, it is recommended to upload large number of files by specifying the path to a directory containing the files.

      Your uploaded files will be shown on the same **File Upload** page in  **sdrf files** and **Fasta files** tabs. Also you can remove the files from workspace.

      ### 3. ⚙️ Analyze your uploaded data

      Select the `sdrf` and `fasta` files for analysis, configure user settings, and start the analysis using the **Run-analysis** button.
      You can terminate the analysis immediately using the **Terminate/Clear** button and you can review the search engine log on the page.
      Once the analysis completed successfully, the output table will be displayed on the page, along with downloadable links for crosslink identification files.

<<<<<<< HEAD
""")
=======
""")
# html_path = Path(st.session_state.workspace)/"results"/"summarypipeline"/"multiqc_report.html"

# if html_path.exists():
#     html_content = html_path.read_text(encoding="utf-8")
#     components.html(html_content, height=800, scrolling=True)

html_path = Path("/app/results/multiqc_report.html")
html_content = html_path.read_text(encoding="utf-8")
components.html(html_content, height=800, scrolling=True)

st.markdown("## Volcano Plot Example using R")

fc_cutoff = st.number_input("Fold Change Cutoff (log2)", value=1.0)
pval_cutoff = st.number_input("P-value Cutoff", value=0.05, format="%.4f")

excel_path = "/data/data2_All_data.xlsx"
sheet_name = "data2"

output_svg = excel_path.replace(".xlsx", "_volcano.svg")

with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False) as tmp_r:
    r_script_path = tmp_r.name
    tmp_r.write(f"""
library(readxl)
library(ggplot2)

data <- read_excel('{excel_path}', sheet = '{sheet_name}')

data <- data[!is.na(data$Dd_FPKM) & !is.na(data$Db_FPKM) & data$Db_FPKM > 0, ]
data$log2FC <- log2(data$Dd_FPKM / data$Db_FPKM)

fc_cutoff <- {fc_cutoff}
pval_cutoff <- {pval_cutoff}
p_cutoff <- -log10({pval_cutoff})

data$group <- "NS"
data$group[data$log2FC > fc_cutoff & -log10(data$`Dd/Db.raw.pval`) > p_cutoff] <- "Up"
data$group[data$log2FC < -fc_cutoff & -log10(data$`Dd/Db.raw.pval`) > p_cutoff] <- "Down"

color_palette <- c("NS" = "gray", "Up" = "red", "Down" = "blue")

volcano_plot <- ggplot(data, aes(x = log2FC, y = -log10(`Dd/Db.raw.pval`), color = group)) +
  geom_point(size = 2, alpha = 0.8) +
  scale_color_manual(values = color_palette) +
  geom_vline(xintercept = c(-fc_cutoff, fc_cutoff), linetype = "dashed", color = "gray") +
  geom_hline(yintercept = p_cutoff, linetype = "dashed", color = "gray") +
  labs(title = "Volcano Plot (FDR based)", x = "log2 Fold Change (N_Dd / N_Db)", y = "-log10 pval") +
  theme_minimal()

ggsave(filename='{output_svg}', plot=volcano_plot, width=8, height=6, dpi=300, device='svg')
                """)
    
subprocess.run(["Rscript", r_script_path], check=True)

st.success("Volcano plot generated!")
st.image(output_svg, use_column_width=True)

os.remove(r_script_path)
>>>>>>> 12a0927 (feat: add support for additional workflow parameters in Configure tab)
