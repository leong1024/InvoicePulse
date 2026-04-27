from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from supabase import Client, create_client

from drift_service.config import DriftServiceSettings


class SupabaseInvoiceUploader:
    def __init__(self, settings: DriftServiceSettings) -> None:
        self._settings = settings
        self._client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

    def verify_access(
        self,
        *,
        table_name: str,
        storage_bucket: str,
    ) -> None:
        self._client.table(table_name).select("id").limit(1).execute()
        self._client.storage.from_(storage_bucket).list(path="", options={"limit": 1})

    def upload_storage_payload(
        self,
        *,
        storage_bucket: str,
        seed: int,
        payload: dict[str, object],
    ) -> str:
        utc_now = datetime.now(timezone.utc)
        object_path = (
            f"extractions/hf-seed-{seed}/{utc_now:%Y/%m/%d}/{uuid4()}.json"
        )
        file_bytes = json.dumps(payload, ensure_ascii=True).encode("utf-8")

        self._client.storage.from_(storage_bucket).upload(
            path=object_path,
            file=file_bytes,
            file_options={"content-type": "application/json", "upsert": "false"},
        )
        return object_path

    def insert_invoice_row(
        self,
        *,
        table_name: str,
        row_payload: dict[str, object],
    ) -> dict[str, object] | None:
        response = self._client.table(table_name).insert(row_payload).execute()
        rows = response.data or []
        return rows[0] if rows else None

    def has_invoice_id(
        self,
        *,
        table_name: str,
        invoice_id: str,
    ) -> bool:
        response = (
            self._client.table(table_name)
            .select("id")
            .eq("invoice_id", invoice_id)
            .limit(1)
            .execute()
        )
        return bool(response.data)
