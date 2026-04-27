from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from supabase import Client, create_client

from drift_service.config import DriftServiceSettings


INVOICE_SELECT_COLUMNS = (
    "id,created_at,vendor,currency,total,status,error,invoice_date"
)


class InvoiceDriftRepository:
    """Small Supabase repository for invoice rows and drift report records."""

    def __init__(self, settings: DriftServiceSettings) -> None:
        self._settings = settings
        self._client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

    def fetch_recent_invoice_rows(self) -> list[dict[str, Any]]:
        response = (
            self._client.table(self._settings.invoice_extractions_table)
            .select(INVOICE_SELECT_COLUMNS)
            .order("created_at", desc=True)
            .order("id", desc=True)
            .limit(self._settings.query_limit)
            .execute()
        )
        return list(response.data or [])

    def insert_drift_report(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        response = (
            self._client.table(self._settings.invoice_drift_reports_table)
            .insert(payload)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def fetch_latest_drift_report(self) -> dict[str, Any] | None:
        response = (
            self._client.table(self._settings.invoice_drift_reports_table)
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def fetch_drift_history(self, limit: int = 30) -> Sequence[dict[str, Any]]:
        safe_limit = max(1, min(limit, 100))
        response = (
            self._client.table(self._settings.invoice_drift_reports_table)
            .select("*")
            .order("created_at", desc=True)
            .limit(safe_limit)
            .execute()
        )
        return response.data or []
