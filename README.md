# QuantMS Web 

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/hjn0415a/quantms-web-test.git
cd quantms-web-test
git checkout -b feature/fastapi-nextflow-host origin/feature/fastapi-nextflow-host
```
### 2. Create a users folder
```bash
mkdir ../users
```
### 3. Place your raw data
Place the `03COVID.raw` file inside the `../users` folder.

### 4. Build the Docker image
```bash
docker build -t quantms-web .
```
### 5. Run the Docker container
```bash
docker run -v ../users:/users --network=host quantms-web
```
### 6. Access the web server
```bash
http://localhost:8501
```
