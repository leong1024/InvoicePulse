from __future__ import annotations

from dataclasses import dataclass
import json
import re
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

    snapshot = report.run(
        reference_data=reference_df,
        current_data=current_df,
    )

    report_dict = _report_to_dict(snapshot)
    summary = _extract_drift_summary(report_dict)

    return DriftAnalysisResult(
        drift_detected=summary["drift_detected"],
        drift_share=summary["drift_share"],
        drifted_columns=summary["drifted_columns"],
        report=report_dict,
        summary=summary,
    )


def _report_to_dict(report_like: Any) -> dict[str, Any]:
    for method_name in ("as_dict", "dict", "model_dump"):
        method = getattr(report_like, method_name, None)
        if callable(method):
            value = method()
            payload = _coerce_dict_payload(value)
            if payload is not None:
                return payload

    for method_name in ("json", "as_json", "model_dump_json"):
        method = getattr(report_like, method_name, None)
        if callable(method):
            value = method()
            payload = _coerce_json_payload(value)
            if payload is not None:
                return payload

    raise TypeError("Unsupported Evidently Report object; cannot serialize report.")


def _coerce_dict_payload(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return _coerce_json_payload(value)
    return None


def _coerce_json_payload(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _extract_drift_summary(report: dict[str, Any]) -> dict[str, Any]:
    modern_summary = _extract_modern_summary(report)
    if modern_summary is not None:
        return modern_summary

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


def _extract_modern_summary(report: dict[str, Any]) -> dict[str, Any] | None:
    metrics = report.get("metrics")
    if not isinstance(metrics, list):
        return None

    has_modern = any(
        isinstance(metric, dict) and "metric_name" in metric and "value" in metric
        for metric in metrics
    )
    if not has_modern:
        return None

    drift_share: float | None = None
    drift_threshold: float | None = None
    drifted_columns: list[str] = []
    columns: list[dict[str, Any]] = []

    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        metric_name = str(metric.get("metric_name", ""))
        value = metric.get("value")

        if metric_name.startswith("DriftedColumnsCount("):
            if isinstance(value, dict):
                drift_share = _safe_float(value.get("share"))
            threshold_match = re.search(r"drift_share=([0-9]*\.?[0-9]+)", metric_name)
            if threshold_match:
                drift_threshold = _safe_float(threshold_match.group(1))
            continue

        parsed = _parse_value_drift_metric(metric_name, value)
        if parsed is None:
            continue
        columns.append(parsed)
        if parsed["drift_detected"]:
            drifted_columns.append(parsed["name"])

    if drift_share is None and columns:
        drift_share = len(drifted_columns) / len(columns)

    threshold = drift_threshold if drift_threshold is not None else 0.5
    drift_detected = (
        drift_share >= threshold if drift_share is not None else bool(drifted_columns)
    )

    return {
        "drift_detected": drift_detected,
        "drift_share": drift_share,
        "drifted_columns": drifted_columns,
        "columns": columns,
    }


def _parse_value_drift_metric(
    metric_name: str,
    value: Any,
) -> dict[str, Any] | None:
    match = re.match(
        r"ValueDrift\(column=(.*?),method=(.*?),threshold=([0-9]*\.?[0-9]+)\)",
        metric_name,
    )
    if not match:
        return None

    column = match.group(1).strip()
    method = match.group(2).strip()
    threshold = _safe_float(match.group(3))
    score = _safe_float(value)

    if score is None or threshold is None:
        drift_detected = False
    elif "p_value" in method.lower():
        drift_detected = score < threshold
    else:
        drift_detected = score > threshold

    return {
        "name": column,
        "drift_detected": drift_detected,
        "score": score,
        "stattest_name": method,
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


def _safe_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None
