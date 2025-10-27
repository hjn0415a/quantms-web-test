# QuantMS Web 

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/hjn0415a/quantms-web-test.git
cd quantms-web-test
git checkout -b feature/fastapi-nextflow-host origin/feature/fastapi-nextflow-host
```
### 2. Create a users/raw folder
Create `users` and `raw` folders under the project root:
```bash
mkdir users
mkdir raw
```
### 3. Place your raw data
Place the raw files(`02COVID.raw` ~ `15COVID.raw`) inside the `raw` folder.

### 4. Build the Docker image
```bash
docker build -t fastapi-nextflow .
```
### 5. Run the Docker container
```bash
docker run -v $(pwd):/app $(pwd)/users:/users --network=host fastapi-nextflow
```
### 6. Access the web server
```bash
http://localhost:8501
```
