# Base Ubuntu image
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git zip unzip build-essential ca-certificates \
    software-properties-common gnupg2 jq cron \
    iproute2 iputils-ping lsb-release apt-transport-https uidmap && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Docker (for DinD)
RUN mkdir -m 0755 -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Install Java via SDKMAN
RUN curl -s "https://get.sdkman.io" | bash && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh && sdk install java 17.0.10-tem" && \
    ln -s /root/.sdkman/candidates/java/current/bin/java /usr/bin/java && \
    echo "export JAVA_HOME=/root/.sdkman/candidates/java/current" >> /etc/profile && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile

ENV JAVA_HOME=/root/.sdkman/candidates/java/current
ENV PATH=$JAVA_HOME/bin:$PATH

# 3. Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && chmod +x /usr/local/bin/nextflow

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

WORKDIR /app
COPY assets/ /app/assets/
COPY content/quantms /app/content/quantms
COPY gdpr_consent/ /app/gdpr_consent
COPY src/ /app/src
COPY app.py /app/app.py
COPY settings.json /app/settings.json
COPY default-parameters.json /app/default-parameters.json
COPY .streamlit/config.toml /app/.streamlit/config.toml

SHELL ["/bin/bash", "-c"]
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'cron' >> /app/entrypoint.sh && \
    echo 'dockerd &' >> /app/entrypoint.sh && \
    echo 'while (! docker info > /dev/null 2>&1); do echo "Waiting for Docker daemon..."; sleep 1; done' >> /app/entrypoint.sh && \
    echo 'exec conda run -n quantms-env streamlit run /app/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose Docker and Streamlit ports
EXPOSE 2375
EXPOSE 8501
ENV PORT=8501
# Docker volume
VOLUME /var/lib/docker

ENTRYPOINT ["/app/entrypoint.sh"]