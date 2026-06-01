# Streamlit Deployment Guide

Entrypoint: `src/dashboard/app.py`.

Before deployment, run:

```bash
python -m src.pipeline.run_all
python scripts/deploy_readiness_check.py
```

The dashboard reads generated CSV/JSON artifacts and does not need external API keys.
