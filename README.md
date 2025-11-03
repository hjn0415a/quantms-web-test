# QuantMS Web 

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/hjn0415a/quantms-web-test.git
cd quantms-web-test
git checkout -b feature/fastapi-nextflow-host origin/feature/fastapi-nextflow-host
```
### 2. Create a users folder
Create `users` and `raw` folders under the project root:
```bash
mkdir users
```
### 3. Build the Docker image
```bash
docker build -t fastapi-nextflow .
```
### 4. Run the Docker container
```bash
docker run -v $(pwd):/app -v $(pwd)/users:/users -p 8501:8501 fastapi-nextflow
```
### 5. Access the web server
```bash
http://localhost:8501
```
