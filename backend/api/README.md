# InvoicePulse API

FastAPI read layer for dashboard data.

## Local Run

Install the drift service and API dependencies, then run:

```bash
$env:PYTHONPATH = "backend/python/drift_service/src;."
uvicorn backend.api.main:app --reload
```

Available endpoints:

- `GET /api/drift/latest`
- `GET /api/drift/history?limit=30`
- `GET /health`
