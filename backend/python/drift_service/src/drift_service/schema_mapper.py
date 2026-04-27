from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any


_AMBIGUOUS_DATE_TOKENS = {"today", "yesterday", "last friday"}
_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%b %d, %Y",
    "%B %d, %Y",
    "%d.%m.%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%m-%Y",
)


@dataclass(frozen=True)
class MappedInvoiceRecord:
    db_payload: dict[str, Any]
    storage_payload: dict[str, Any]
    warnings: list[str]


def map_hf_row_to_invoice_record(
    *,
    row: dict[str, Any],
    invoice_id: str,
    model_name: str,
) -> MappedInvoiceRecord:
    warnings: list[str] = []
    source_text = _to_text(row.get("input"))
    parsed_output = _parse_output_json(row.get("output"), warnings)

    vendor = _to_text(parsed_output.get("vendor"))
    currency = _normalize_currency(parsed_output.get("currency"))
    total = _to_float(parsed_output.get("total"))
    invoice_date, date_warning = _normalize_date(parsed_output.get("date"))
    if date_warning:
        warnings.append(date_warning)

    status = "success"
    if not vendor or not currency or total is None:
        status = "partial"
        warnings.append("Missing one or more key fields: vendor/currency/total.")

    storage_payload = {
        "source": {
            "instruction": row.get("instruction"),
            "input": source_text,
        },
        "parsed": parsed_output,
        "normalized_invoice": {
            "invoice_id": invoice_id,
            "vendor": vendor,
            "invoice_date": invoice_date,
            "total": total,
            "currency": currency,
        },
        "mapping_warnings": warnings,
    }

    db_payload = {
        "source_text": source_text,
        "image_url": None,
        "image_storage_bucket": None,
        "image_storage_path": None,
        "result_storage_bucket": "invoice-extractions",
        "result_storage_path": None,
        "invoice_id": invoice_id,
        "vendor": vendor,
        "invoice_date": invoice_date,
        "total": total,
        "currency": currency,
        "model": model_name,
        "status": status,
        "error": "; ".join(warnings) if warnings else None,
    }

    return MappedInvoiceRecord(
        db_payload=db_payload,
        storage_payload=storage_payload,
        warnings=warnings,
    )


def _parse_output_json(output_value: Any, warnings: list[str]) -> dict[str, Any]:
    if isinstance(output_value, dict):
        return output_value
    if not output_value:
        warnings.append("Dataset output is empty.")
        return {}
    try:
        return json.loads(str(output_value))
    except json.JSONDecodeError:
        warnings.append("Dataset output is not valid JSON.")
        return {}


def _normalize_currency(value: Any) -> str:
    text = _to_text(value).upper()
    return text[:3] if text else ""


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_date(value: Any) -> tuple[str | None, str | None]:
    text = _to_text(value)
    if not text:
        return None, "Date missing from parsed output."
    lowered = text.lower()
    if lowered in _AMBIGUOUS_DATE_TOKENS:
        return None, f"Ambiguous date value '{text}' set to null."

    candidate = _strip_ordinal_suffix(text)
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(candidate, fmt)
            return parsed.strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    return None, f"Unparseable date value '{text}' set to null."


def _strip_ordinal_suffix(text: str) -> str:
    return re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", text.strip(), flags=re.I)


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
