# Invoice Drift Dashboard Runbook

## What It Monitors

The drift job reads `public.invoice_extractions`, takes the newest 120 rows, and
compares:

- current window: newest 20 rows
- reference window: next 100 rows

It runs Evidently `DataDriftPreset` and stores a summarized report in
`public.invoice_drift_reports`.

## Setup

1. Apply Supabase migrations, including
   `supabase/migrations/0002_invoice_drift_reports.sql`.
2. Configure backend environment variables:

```bash
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

3. Install the Python drift service:

```bash
cd backend/python/drift_service
pip install -e ".[test]"
```

4. Run a drift computation:

```bash
invoicepulse-drift-run
```

## API

Run the FastAPI app from the repository root:

```bash
$env:PYTHONPATH = "backend/python/drift_service/src;."
uvicorn backend.api.main:app --reload
```

Endpoints:

- `GET /api/drift/latest`
- `GET /api/drift/history?limit=30`

## Frontend

Run the React dashboard:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` if the API is not running at `http://localhost:8000`.

## Scheduling

For a first production pass, run `invoicepulse-drift-run` on an hourly scheduler
such as GitHub Actions cron, a VM cron task, or a platform scheduler. Each run
stores a new report row so the dashboard can show history.

## Troubleshooting

- `insufficient_data`: fewer than 120 invoice extraction rows exist.
- `error`: the drift job failed; inspect `invoice_drift_reports.error`.
- Empty dashboard: run the drift job once and confirm the API can access
  `invoice_drift_reports`.
- Supabase permission failures: use the service role key only in trusted
  backend environments and keep it out of the React app.
