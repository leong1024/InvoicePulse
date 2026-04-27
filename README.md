# InvoicePulse

InvoicePulse monitors Supabase invoice extraction records and surfaces drift in a
React dashboard with a notebook-style interface.

## Main Parts

- `backend/python/drift_service`: Supabase query pipeline and Evidently drift job.
- `backend/api`: FastAPI read API for the dashboard.
- `frontend`: React + TypeScript dashboard.
- `supabase/migrations`: database schema changes.
- `docs`: schema notes and operational runbook.

## Drift Rule

The drift job queries the newest 120 rows from `public.invoice_extractions`.
It compares the newest 20 rows against the next 100 rows, excluding those newest
20 rows from the reference set.

## Start Locally

See `docs/drift-dashboard-runbook.md` for setup, environment variables, and run
commands.
