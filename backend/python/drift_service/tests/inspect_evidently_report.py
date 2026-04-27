from __future__ import annotations

import json

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


def main() -> None:
    reference_df = pd.DataFrame(
        {
            "vendor": ["Adobe", "Uber", "Dell", "Target", "Steam"],
            "currency": ["USD", "USD", "EUR", "EUR", "GBP"],
            "status": ["success", "success", "success", "partial", "success"],
            "total": [100.0, 210.5, 330.2, 95.1, 520.0],
            "has_error": [False, False, False, True, False],
            "missing_total": [False, False, False, False, False],
            "missing_invoice_date": [False, False, True, False, False],
        }
    )
    current_df = pd.DataFrame(
        {
            "vendor": ["IKEA", "IKEA", "Uber", "Adobe"],
            "currency": ["JPY", "JPY", "EUR", "USD"],
            "status": ["error", "error", "success", "success"],
            "total": [1400.0, 950.0, 250.0, 110.0],
            "has_error": [True, True, False, False],
            "missing_total": [False, False, False, False],
            "missing_invoice_date": [True, True, False, False],
        }
    )

    report = Report(metrics=[DataDriftPreset()])
    snapshot = report.run(reference_data=reference_df, current_data=current_df)

    print("Snapshot type:", type(snapshot))
    print(
        "Snapshot methods:",
        [name for name in ("dict", "json", "model_dump") if hasattr(snapshot, name)],
    )

    payload = snapshot.dict() if hasattr(snapshot, "dict") else {}
    metrics = payload.get("metrics", [])
    print("Top-level keys:", list(payload.keys()))
    print("Metrics count:", len(metrics))
    if metrics:
        first_metric = metrics[0]
        print("First metric keys:", list(first_metric.keys()))
        print("First metric name:", first_metric.get("metric_name"))
        print("First metric value:", json.dumps(first_metric.get("value"), indent=2))

    print("Payload sample:")
    print(json.dumps(payload, indent=2, default=str)[:2500])


if __name__ == "__main__":
    main()
