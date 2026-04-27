from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


DriftStatus = Literal["success", "insufficient_data", "error", "not_available"]


class DriftColumnSummary(BaseModel):
    name: str
    drift_detected: bool = False
    score: float | None = None
    stattest_name: str | None = None


class DriftStatusResponse(BaseModel):
    status: DriftStatus
    computed_at: str | None
    drift_flag: bool
    drift_share: float | None
    drifted_columns: list[str] = Field(default_factory=list)
    reference_count: int
    current_count: int
    insufficient_data: bool
    error: str | None
    flag_reason: str | None = None
    columns: list[DriftColumnSummary] = Field(default_factory=list)


class DriftHistoryResponse(BaseModel):
    reports: list[DriftStatusResponse]


class DriftRunResponse(BaseModel):
    status: DriftStatus
    computed_at: str | None
    drift_flag: bool
    message: str


def drift_response_from_report(row: dict[str, Any] | None) -> DriftStatusResponse:
    if row is None:
        return DriftStatusResponse(
            status="not_available",
            computed_at=None,
            drift_flag=False,
            drift_share=None,
            drifted_columns=[],
            reference_count=0,
            current_count=0,
            insufficient_data=True,
            error=None,
            flag_reason="No drift report has been generated yet.",
            columns=[],
        )

    summary = row.get("summary_json") or {}
    status = row.get("status") or summary.get("status") or "error"

    return DriftStatusResponse(
        status=status,
        computed_at=row.get("created_at"),
        drift_flag=bool(row.get("drift_detected")),
        drift_share=_as_float(row.get("drift_share")),
        drifted_columns=list(row.get("drifted_columns") or []),
        reference_count=int(row.get("reference_count") or 0),
        current_count=int(row.get("current_count") or 0),
        insufficient_data=status == "insufficient_data",
        error=row.get("error"),
        flag_reason=summary.get("flag_reason"),
        columns=[
            DriftColumnSummary(**column)
            for column in summary.get("columns", [])
            if isinstance(column, dict)
        ],
    )


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def drift_run_response_from_report(row: dict[str, Any] | None) -> DriftRunResponse:
    report = drift_response_from_report(row)
    message = {
        "success": "Drift analysis completed.",
        "insufficient_data": "Drift run finished with insufficient baseline rows.",
        "error": "Drift run failed. Check latest report details.",
        "not_available": "Drift run did not return a report.",
    }.get(report.status, "Drift run completed.")

    return DriftRunResponse(
        status=report.status,
        computed_at=report.computed_at,
        drift_flag=report.drift_flag,
        message=message,
    )
