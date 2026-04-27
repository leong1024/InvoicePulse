from __future__ import annotations

from fastapi import APIRouter, Query

from backend.api.schemas import (
    DriftHistoryResponse,
    DriftRunResponse,
    DriftStatusResponse,
    drift_run_response_from_report,
    drift_response_from_report,
)
from drift_service.config import get_settings
from drift_service.run_once import run_once
from drift_service.supabase_client import InvoiceDriftRepository


router = APIRouter(prefix="/api/drift", tags=["drift"])


def _repository() -> InvoiceDriftRepository:
    return InvoiceDriftRepository(get_settings())


@router.get("/latest", response_model=DriftStatusResponse)
def latest_drift_report() -> DriftStatusResponse:
    report = _repository().fetch_latest_drift_report()
    return drift_response_from_report(report)


@router.get("/history", response_model=DriftHistoryResponse)
def drift_history(
    limit: int = Query(default=30, ge=1, le=100),
) -> DriftHistoryResponse:
    reports = _repository().fetch_drift_history(limit=limit)
    return DriftHistoryResponse(
        reports=[drift_response_from_report(report) for report in reports]
    )


@router.post("/run", response_model=DriftRunResponse)
def run_drift_analysis() -> DriftRunResponse:
    run_once()
    latest = _repository().fetch_latest_drift_report()
    return drift_run_response_from_report(latest)
