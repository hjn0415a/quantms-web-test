# quantms-streamlit template 

## How to build

- docker build -t quantms-dind .
- docker run --privileged --cgroupns=host -p 8501:8501 -p 2375:2375 -v ${pwd}:/workspace --name quantms-container quantms-dind
