from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from typing import Any

from datasets import load_dataset

from drift_service.config import get_settings
from drift_service.schema_mapper import map_hf_row_to_invoice_record
from drift_service.supabase_uploader import SupabaseInvoiceUploader


HF_DATASET_NAME = "manuelaschrittwieser/invoice-extraction-dataset-v2"
HF_DATASET_SPLIT = "train"
DEFAULT_SAMPLE_SIZE = 300
DEFAULT_SEED = 42
DEFAULT_MODEL_NAME = "hf-invoice-dataset-v2"
DEFAULT_STORAGE_BUCKET = "invoice-extractions"


@dataclass
class IngestionSummary:
    sampled_rows: int = 0
    inserted_rows: int = 0
    partial_rows: int = 0
    failed_rows: int = 0
    skipped_duplicates: int = 0


def run_loader(
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    seed: int = DEFAULT_SEED,
    table_name: str | None = None,
    storage_bucket: str = DEFAULT_STORAGE_BUCKET,
    model_name: str = DEFAULT_MODEL_NAME,
) -> IngestionSummary:
    settings = get_settings()
    uploader = SupabaseInvoiceUploader(settings)
    target_table = table_name or settings.invoice_extractions_table
    uploader.verify_access(table_name=target_table, storage_bucket=storage_bucket)

    sampled_rows = _sample_rows(sample_size=sample_size, seed=seed)
    summary = IngestionSummary(sampled_rows=len(sampled_rows))

    for idx, row in enumerate(sampled_rows):
        try:
            invoice_id = f"HF-{seed}-{idx:04d}"
            mapped = map_hf_row_to_invoice_record(
                row=row,
                invoice_id=invoice_id,
                model_name=model_name,
            )

            payload = dict(mapped.db_payload)
            payload["result_storage_bucket"] = storage_bucket

            if uploader.has_invoice_id(table_name=target_table, invoice_id=invoice_id):
                summary.skipped_duplicates += 1
                continue

            object_path = uploader.upload_storage_payload(
                storage_bucket=storage_bucket,
                seed=seed,
                payload=mapped.storage_payload,
            )
            payload["result_storage_path"] = object_path
            uploader.insert_invoice_row(table_name=target_table, row_payload=payload)

            summary.inserted_rows += 1
            if payload.get("status") == "partial":
                summary.partial_rows += 1
        except Exception:
            summary.failed_rows += 1

    return summary


def _sample_rows(*, sample_size: int, seed: int) -> list[dict[str, Any]]:
    dataset = load_dataset(HF_DATASET_NAME, split=HF_DATASET_SPLIT)
    all_rows = [dict(row) for row in dataset]

    unique_rows: list[dict[str, Any]] = []
    seen_inputs: set[str] = set()
    for row in all_rows:
        key = str(row.get("input", "")).strip()
        if key in seen_inputs:
            continue
        seen_inputs.add(key)
        unique_rows.append(row)

    if sample_size > len(unique_rows):
        raise ValueError(
            f"Requested sample size {sample_size} exceeds available unique rows "
            f"{len(unique_rows)}."
        )

    rng = random.Random(seed)
    return rng.sample(unique_rows, sample_size)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sample HF invoice rows and upload them into Supabase.",
    )
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--table-name", type=str, default=None)
    parser.add_argument("--storage-bucket", type=str, default=DEFAULT_STORAGE_BUCKET)
    parser.add_argument("--model-name", type=str, default=DEFAULT_MODEL_NAME)
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    summary = run_loader(
        sample_size=args.sample_size,
        seed=args.seed,
        table_name=args.table_name,
        storage_bucket=args.storage_bucket,
        model_name=args.model_name,
    )
    print(json.dumps(summary.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
