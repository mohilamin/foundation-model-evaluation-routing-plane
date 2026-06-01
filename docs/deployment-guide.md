# Deployment Guide

## Local Prototype

```bash
conda create -n model-routing-plane python=3.12 -y
conda activate model-routing-plane
pip install -r requirements.txt
python -m src.pipeline.run_all
streamlit run src/dashboard/app.py
uvicorn src.api.main:app --reload
```

## Streamlit Community Cloud

- Push the repo to GitHub.
- Deploy from Streamlit Community Cloud.
- Entrypoint: `src/dashboard/app.py`.
- Requirements: `requirements.txt`.
- No secrets required.

## FastAPI Docker

```bash
docker build -t model-routing-plane-api .
docker run -p 8000:8000 model-routing-plane-api
```
