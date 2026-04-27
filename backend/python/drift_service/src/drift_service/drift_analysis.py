from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


@dataclass(frozen=True)
class DriftAnalysisResult:
    drift_detected: bool
    drift_share: float | None
    drifted_columns: list[str]
    report: dict[str, Any]
    summary: dict[str, Any]


def run_drift_analysis(
    *,
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> DriftAnalysisResult:
    report = Report(metrics=[DataDriftPreset()])

    report.run(
        reference_data=reference_df,
        current_data=current_df,
    )

    report_dict = _report_to_dict(report)
    summary = _extract_drift_summary(report_dict)

    return DriftAnalysisResult(
        drift_detected=summary["drift_detected"],
        drift_share=summary["drift_share"],
        drifted_columns=summary["drifted_columns"],
        report=report_dict,
        summary=summary,
    )


def _report_to_dict(report: Report) -> dict[str, Any]:
    if hasattr(report, "as_dict"):
        return report.as_dict()
    if hasattr(report, "dict"):
        return report.dict()
    raise TypeError("Unsupported Evidently Report object; cannot serialize report.")


def _extract_drift_summary(report: dict[str, Any]) -> dict[str, Any]:
    metric_results = _metric_results(report)
    dataset_result = _first_dataset_drift_result(metric_results)
    column_results = _column_drift_results(metric_results)

    drifted_columns = [
        column
        for column, result in column_results.items()
        if _is_drifted(result)
    ]

    drift_share = _first_number(
        dataset_result,
        keys=("share_of_drifted_columns", "drift_share"),
    )
    drift_detected = bool(
        _first_value(
            dataset_result,
            keys=("dataset_drift", "drift_detected"),
            default=bool(drifted_columns),
        )
    )

    return {
        "drift_detected": drift_detected,
        "drift_share": drift_share,
        "drifted_columns": drifted_columns,
        "columns": [
            {
                "name": column,
                "drift_detected": _is_drifted(result),
                "score": _first_number(
                    result,
                    keys=("drift_score", "stattest_result", "score"),
                ),
                "stattest_name": _first_value(
                    result,
                    keys=("stattest_name", "stattest"),
                    default=None,
                ),
            }
            for column, result in column_results.items()
        ],
    }


def _metric_results(report: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = report.get("metrics")
    if isinstance(metrics, list):
        return [
            metric.get("result", {})
            for metric in metrics
            if isinstance(metric, dict)
        ]
    return []


def _first_dataset_drift_result(
    metric_results: list[dict[str, Any]],
) -> dict[str, Any]:
    for result in metric_results:
        if "dataset_drift" in result or "share_of_drifted_columns" in result:
            return result
    return {}


def _column_drift_results(
    metric_results: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    for result in metric_results:
        drift_by_columns = result.get("drift_by_columns")
        if isinstance(drift_by_columns, dict):
            return {
                str(column): column_result
                for column, column_result in drift_by_columns.items()
                if isinstance(column_result, dict)
            }
    return {}


def _is_drifted(result: dict[str, Any]) -> bool:
    return bool(
        _first_value(
            result,
            keys=("drift_detected", "drifted"),
            default=False,
        )
    )


def _first_number(
    source: dict[str, Any],
    *,
    keys: tuple[str, ...],
) -> float | None:
    value = _first_value(source, keys=keys, default=None)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return _first_number(value, keys=keys)
    return None


def _first_value(
    source: dict[str, Any],
    *,
    keys: tuple[str, ...],
    default: Any,
) -> Any:
    for key in keys:
        if key in source:
            return source[key]
    for value in source.values():
        if isinstance(value, dict):
            nested = _first_value(value, keys=keys, default=None)
            if nested is not None:
                return nested
    return default
