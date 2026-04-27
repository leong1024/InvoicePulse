import pandas as pd

from drift_service import drift_analysis


def test_run_drift_analysis_extracts_dataset_and_column_summary(monkeypatch) -> None:
    class FakeReport:
        def __init__(self, metrics):
            self.metrics = metrics

        def run(self, reference_data, current_data):
            self.reference_data = reference_data
            self.current_data = current_data

        def as_dict(self):
            return {
                "metrics": [
                    {
                        "result": {
                            "dataset_drift": True,
                            "share_of_drifted_columns": 0.5,
                            "drift_by_columns": {
                                "vendor": {
                                    "drift_detected": True,
                                    "drift_score": 0.01,
                                    "stattest_name": "chisquare",
                                },
                                "total": {
                                    "drift_detected": False,
                                    "drift_score": 0.8,
                                    "stattest_name": "ks",
                                },
                            },
                        }
                    }
                ]
            }

    monkeypatch.setattr(drift_analysis, "Report", FakeReport)
    monkeypatch.setattr(drift_analysis, "DataDriftPreset", lambda: object())

    result = drift_analysis.run_drift_analysis(
        reference_df=pd.DataFrame({"vendor": ["A"], "total": [10]}),
        current_df=pd.DataFrame({"vendor": ["B"], "total": [11]}),
    )

    assert result.drift_detected is True
    assert result.drift_share == 0.5
    assert result.drifted_columns == ["vendor"]
    assert result.summary["columns"][0]["stattest_name"] == "chisquare"
