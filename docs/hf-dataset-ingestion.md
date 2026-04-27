# Hugging Face Dataset Ingestion

This command samples 300 rows from:

- `manuelaschrittwieser/invoice-extraction-dataset-v2` (split: `train`)

and uploads them to:

- Supabase Storage bucket `invoice-extractions` (JSON artifacts)
- Supabase table `public.invoice_extractions` (flattened rows)

## Prerequisites

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set in environment or `.env`.
- Table `public.invoice_extractions` and bucket `invoice-extractions` exist.

## Install

```bash
cd backend/python/drift_service
pip install -e ".[test]"
```

## Run

```bash
invoicepulse-hf-load --sample-size 300 --seed 42
```

Equivalent module run:

```bash
python -m drift_service.test_dataset_loader --sample-size 300 --seed 42
```

Optional flags:

- `--table-name invoice_extractions`
- `--storage-bucket invoice-extractions`
- `--model-name hf-invoice-dataset-v2`

## Mapping Behavior

- Uses dataset `output` JSON as canonical parsed values.
- Maps to schema fields: `invoice_id`, `vendor`, `invoice_date`, `total`, `currency`.
- `invoice_id` is deterministic: `HF-<seed>-<idx>`.
- Date normalization:
  - Parses structured formats to `YYYY-MM-DD`.
  - Sets `invoice_date = null` for ambiguous values like `yesterday` or `last Friday`.
- Marks row `status = partial` if vendor/currency/total is missing.

## Idempotency

- Script checks `invoice_id` before insert and skips duplicates.

## Validation Query

```sql
select id, created_at, invoice_id, vendor, invoice_date, total, currency, status
from public.invoice_extractions
where invoice_id like 'HF-%'
order by created_at desc
limit 50;
```

## Cleanup Test Data

```sql
delete from public.invoice_extractions
where invoice_id like 'HF-%';
```
