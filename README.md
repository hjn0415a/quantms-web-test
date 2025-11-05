# QuantMS Web 

## Installation
### 1. Nextflow Installation
### Requirements
Nextflow requires Bash 3.2 (or later) and Java 17 (or later, up to 25) to be installed.
To install Java with SDKMAN:

1. Install SDKMAN:
   ```bash
   curl -s https://get.sdkman.io | bash
   ```
2. Open a new terminal
3. Install Java:
   ```bash
   sdk install java 17.0.10-tem
   ```
4. Confirm that Java is installed correctly:
   ```bash
   java -version
   ```
### Install Nextflow
1. Download Nextflow:
    ```bash
    curl -s https://get.nextflow.io | bash
    ```
2. Move Nextflow into an executable path.
    ```bash
    sudo mv nextflow /usr/local/bin
    ```
3. Confirm Nextflow is installed correctly:
    ```bash
    nextflow info
    ```
    
> Installation steps are based on the official [Nextflow documentation](https://www.nextflow.io/docs/latest/install.html).
> 

### 2. Run FastAPI Server
```bash
# Clone the repository
git clone https://github.com/hjn0415a/quantms-web-test.git
cd quantms-web-test

# Initialize submodules
git submodule update --init --recursive

# Create and activate a virtual environment
cd backend/fastapi-nextflow-host
python -m venv fastapi-env
source fastapi-env/bin/activate # On Windows: fastapi-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# run fastapi server
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```
### 3. Run the Streamlit App
After opening a new terminal, run the following command from the **project root directory**:
```bash
docker-compose up --build
```
### 4. Access the web server
Open your browser and go to:
```bash
http://localhost:8501
```
