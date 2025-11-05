# Base Ubuntu image
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git zip unzip build-essential ca-certificates \
    software-properties-common gnupg2 jq cron openssh-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Java via SDKMAN (for compatibility if any Java tools needed)
RUN curl -s "https://get.sdkman.io" | bash && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh && sdk install java 17.0.10-tem" && \
    ln -s /root/.sdkman/candidates/java/current/bin/java /usr/bin/java && \
    echo "export JAVA_HOME=/root/.sdkman/candidates/java/current" >> /etc/profile && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profiled

ENV JAVA_HOME=/root/.sdkman/candidates/java/current
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Miniforge (conda)
RUN wget -q https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O miniforge.sh && \
    bash miniforge.sh -b -p /opt/conda && \
    rm miniforge.sh
ENV PATH="/opt/conda/bin:$PATH"

# Create Conda environment
RUN conda install -y mamba -n base -c conda-forge && \
    mamba create -y -n quantms-env python=3.10 && \
    conda clean -afy

# Install Python dependencies
COPY requirements.txt .
SHELL ["conda", "run", "-n", "quantms-env", "/bin/bash", "-c"]
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
WORKDIR /app
# COPY assets/ /app/assets/
# COPY content/ /app/content
# COPY gdpr_consent/ /app/gdpr_consent
# COPY src/ /app/src
# COPY app.py /app/app.py
# COPY data/ /app/data
# COPY settings.json /app/settings.json
# COPY default-values.json /app/default-values.json
# COPY default-parameters.json /app/default-parameters.json
# COPY .streamlit/config.toml /app/.streamlit/config.toml

# Add entrypoint script
SHELL ["/bin/bash", "-c"]
RUN mkdir -p /entry && \
    echo '#!/bin/bash' > /entry/entrypoint.sh && \
    echo 'cron' >> /entry/entrypoint.sh && \
    echo 'exec conda run -n quantms-env streamlit run /app/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0' >> /entry/entrypoint.sh && \
    chmod +x /entry/entrypoint.sh

EXPOSE 8501
ENV PORT=8501

ENTRYPOINT ["/entry/entrypoint.sh"]