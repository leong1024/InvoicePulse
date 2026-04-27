from drift_service.window_builder import build_drift_windows


def test_build_drift_windows_uses_latest_20_and_prior_100() -> None:
    rows = [_row(index) for index in range(120)]

    windows = build_drift_windows(rows)

    assert windows.has_sufficient_data
    assert windows.current_count == 20
    assert windows.reference_count == 100
    assert windows.current_df["vendor"].tolist()[0] == "Vendor 0"
    assert windows.current_df["vendor"].tolist()[-1] == "Vendor 19"
    assert windows.reference_df["vendor"].tolist()[0] == "Vendor 20"
    assert windows.reference_df["vendor"].tolist()[-1] == "Vendor 119"


def test_build_drift_windows_returns_insufficient_data() -> None:
    windows = build_drift_windows([_row(index) for index in range(25)])

    assert not windows.has_sufficient_data
    assert windows.status == "insufficient_data"
    assert windows.current_count == 20
    assert windows.reference_count == 5
    assert "Need 120 invoice rows" in str(windows.error)


def test_build_drift_windows_normalizes_missing_quality_fields() -> None:
    rows = [_row(index) for index in range(120)]
    rows[0]["total"] = None
    rows[0]["invoice_date"] = None
    rows[0]["error"] = "failed parse"
    rows[0]["vendor"] = ""

    windows = build_drift_windows(rows)

    current_row = windows.current_df.iloc[0]
    assert current_row["vendor"] == "__missing__"
    assert current_row["missing_total"]
    assert current_row["missing_invoice_date"]
    assert current_row["has_error"]


def _row(index: int) -> dict[str, object]:
    return {
        "id": f"row-{index}",
        "created_at": f"2026-04-27T00:{index:02d}:00Z",
        "vendor": f"Vendor {index}",
        "currency": "USD",
        "total": index + 0.5,
        "status": "success",
        "error": None,
        "invoice_date": "2026-04-27",
    }
