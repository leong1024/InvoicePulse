from __future__ import annotations

from typing import Any

from drift_service.drift_analysis import DriftAnalysisResult
from drift_service.window_builder import DriftWindows


def build_success_report_payload(
    *,
    windows: DriftWindows,
    analysis: DriftAnalysisResult,
) -> dict[str, Any]:
    return {
        "reference_count": windows.reference_count,
        "current_count": windows.current_count,
        "drift_detected": analysis.drift_detected,
        "drift_share": analysis.drift_share,
        "drifted_columns": analysis.drifted_columns,
        "report_json": analysis.report,
        "summary_json": {
            **analysis.summary,
            "status": "success",
            "flag_reason": _flag_reason(
                analysis.drift_detected,
                analysis.drifted_columns,
            ),
        },
        "status": "success",
        "error": None,
    }


def build_insufficient_data_payload(windows: DriftWindows) -> dict[str, Any]:
    return {
        "reference_count": windows.reference_count,
        "current_count": windows.current_count,
        "drift_detected": False,
        "drift_share": None,
        "drifted_columns": [],
        "report_json": {},
        "summary_json": {
            "status": "insufficient_data",
            "drift_detected": False,
            "drift_share": None,
            "drifted_columns": [],
            "columns": [],
            "flag_reason": windows.error,
        },
        "status": "insufficient_data",
        "error": windows.error,
    }


def build_error_payload(error: Exception) -> dict[str, Any]:
    message = str(error)
    return {
        "reference_count": 0,
        "current_count": 0,
        "drift_detected": False,
        "drift_share": None,
        "drifted_columns": [],
        "report_json": {},
        "summary_json": {
            "status": "error",
            "drift_detected": False,
            "drift_share": None,
            "drifted_columns": [],
            "columns": [],
            "flag_reason": message,
        },
        "status": "error",
        "error": message,
    }


def _flag_reason(drift_detected: bool, drifted_columns: list[str]) -> str:
    if not drift_detected:
        return "No dataset drift detected in the latest invoice window."
    if not drifted_columns:
        return "Dataset drift detected."
    return "Dataset drift detected in: " + ", ".join(drifted_columns)
