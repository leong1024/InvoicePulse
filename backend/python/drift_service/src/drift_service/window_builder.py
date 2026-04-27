from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


DRIFT_COLUMNS = [
    "vendor",
    "currency",
    "status",
    "total",
    "has_error",
    "missing_total",
    "missing_invoice_date",
]


@dataclass(frozen=True)
class DriftWindows:
    reference_df: pd.DataFrame
    current_df: pd.DataFrame
    reference_count: int
    current_count: int
    status: str
    error: str | None = None

    @property
    def has_sufficient_data(self) -> bool:
        return self.status == "ready"


def build_drift_windows(
    rows: list[dict[str, Any]],
    *,
    current_window_size: int = 20,
    reference_window_size: int = 100,
) -> DriftWindows:
    required_rows = current_window_size + reference_window_size
    if len(rows) < required_rows:
        return DriftWindows(
            reference_df=pd.DataFrame(columns=DRIFT_COLUMNS),
            current_df=pd.DataFrame(columns=DRIFT_COLUMNS),
            reference_count=max(0, len(rows) - current_window_size),
            current_count=min(len(rows), current_window_size),
            status="insufficient_data",
            error=(
                f"Need {required_rows} invoice rows for drift analysis; "
                f"found {len(rows)}."
            ),
        )

    current_rows = rows[:current_window_size]
    reference_rows = rows[current_window_size:required_rows]

    return DriftWindows(
        reference_df=_to_drift_frame(reference_rows),
        current_df=_to_drift_frame(current_rows),
        reference_count=len(reference_rows),
        current_count=len(current_rows),
        status="ready",
    )


def _to_drift_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame([_normalize_row(row) for row in rows])
    if frame.empty:
        return pd.DataFrame(columns=DRIFT_COLUMNS)
    return frame[DRIFT_COLUMNS]


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    total = pd.to_numeric(row.get("total"), errors="coerce")
    invoice_date = row.get("invoice_date")
    error = row.get("error")

    return {
        "vendor": _normalize_category(row.get("vendor")),
        "currency": _normalize_category(row.get("currency")),
        "status": _normalize_category(row.get("status")),
        "total": total,
        "has_error": bool(error),
        "missing_total": pd.isna(total),
        "missing_invoice_date": invoice_date in (None, ""),
    }


def _normalize_category(value: Any) -> str:
    if value is None:
        return "__missing__"
    normalized = str(value).strip()
    return normalized if normalized else "__missing__"
