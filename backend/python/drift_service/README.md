# InvoicePulse Drift Service

Python service that compares the most recent invoice extraction records with a
stable reference window and stores Evidently drift reports back in Supabase.

## Window Definition

- Current data: newest 20 rows from `public.invoice_extractions`
- Reference data: next newest 100 rows, excluding the current window
- Ordering: `created_at DESC, id DESC`

## Required Environment

```bash
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

Use the service role key only in trusted backend or scheduled job environments.

## Run Once

```bash
pip install -e ".[test]"
invoicepulse-drift-run
```

The command writes a row into `public.invoice_drift_reports` with either a
successful Evidently summary, an insufficient-data status, or an error status.
