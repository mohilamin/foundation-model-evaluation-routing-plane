# FastAPI Docker Deployment Guide

Build and run:

```bash
docker build -t model-routing-plane-api .
docker run -p 8000:8000 model-routing-plane-api
```

The default container command serves `src.api.main:app` with Uvicorn.
