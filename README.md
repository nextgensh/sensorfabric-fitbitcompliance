# sensorfabric-fitbitcompliance
A Python dash application that shows sensorfabric users compliance metrics on users wearing FitBit devices. 

# Runing it 
```bash
export AWS_ACCESS_KEY=...
export AWS_SECRET_KEY=...
# Create a virtual python environment. If you are pushing this to RStudioConnect make sure the server and local python versions match exactly.
python3 -m venv .env
# Activate the virtual environment.
source .env/bin/activate 
pip3 install -f requirements.txt
python3 app.py
```

# AWS Services used
This application closely relies on the following AWS services to correctly work. 
* Secrets Manager.
* AWS S3
* AWS Athena

This tool will require a deployed sensorfabric AWS backend to correctly function.
Please contact us if you are interested in doing so at shravanaras@arizona.edu
