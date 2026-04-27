from __future__ import annotations

import json
import sys

from drift_service.config import get_settings
from drift_service.drift_analysis import run_drift_analysis
from drift_service.report_serializer import (
    build_error_payload,
    build_insufficient_data_payload,
    build_success_report_payload,
)
from drift_service.supabase_client import InvoiceDriftRepository
from drift_service.window_builder import build_drift_windows


def run_once() -> dict[str, object] | None:
    settings = get_settings()
    repository = InvoiceDriftRepository(settings)

    try:
        rows = repository.fetch_recent_invoice_rows()
        windows = build_drift_windows(
            rows,
            current_window_size=settings.current_window_size,
            reference_window_size=settings.reference_window_size,
        )

        if not windows.has_sufficient_data:
            payload = build_insufficient_data_payload(windows)
        else:
            analysis = run_drift_analysis(
                reference_df=windows.reference_df,
                current_df=windows.current_df,
            )
            payload = build_success_report_payload(
                windows=windows,
                analysis=analysis,
            )
    except Exception as exc:  # Store failed runs so the dashboard can explain them.
        payload = build_error_payload(exc)

    return repository.insert_drift_report(payload)


def main() -> int:
    inserted = run_once()
    print(json.dumps(inserted, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
