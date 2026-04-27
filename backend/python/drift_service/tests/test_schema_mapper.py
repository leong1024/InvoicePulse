from drift_service.schema_mapper import map_hf_row_to_invoice_record


def test_mapper_parses_valid_json_and_normalizes_fields() -> None:
    mapped = map_hf_row_to_invoice_record(
        row={
            "instruction": "Extract invoice details into JSON.",
            "input": "Invoice from Adobe for 2 Groceries.",
            "output": (
                '{"item":"Groceries","quantity":2,"date":"2023-10-12",'
                '"vendor":"Adobe","total":2318.98,"currency":"jpy"}'
            ),
        },
        invoice_id="HF-42-0001",
        model_name="hf-invoice-dataset-v2",
    )

    assert mapped.db_payload["vendor"] == "Adobe"
    assert mapped.db_payload["currency"] == "JPY"
    assert mapped.db_payload["invoice_date"] == "2023-10-12"
    assert mapped.db_payload["total"] == 2318.98
    assert mapped.db_payload["status"] == "success"
    assert mapped.db_payload["error"] is None


def test_mapper_sets_null_for_ambiguous_dates() -> None:
    mapped = map_hf_row_to_invoice_record(
        row={
            "instruction": "Extract invoice details into JSON.",
            "input": "Spent 100 USD yesterday at Adobe.",
            "output": (
                '{"date":"yesterday","vendor":"Adobe",'
                '"total":100,"currency":"usd"}'
            ),
        },
        invoice_id="HF-42-0002",
        model_name="hf-invoice-dataset-v2",
    )

    assert mapped.db_payload["invoice_date"] is None
    assert mapped.db_payload["status"] == "success"
    assert "Ambiguous date value" in (mapped.db_payload["error"] or "")


def test_mapper_marks_partial_when_key_fields_missing() -> None:
    mapped = map_hf_row_to_invoice_record(
        row={
            "instruction": "Extract invoice details into JSON.",
            "input": "Invalid invoice output.",
            "output": '{"date":"2023-10-12","vendor":"Adobe"}',
        },
        invoice_id="HF-42-0003",
        model_name="hf-invoice-dataset-v2",
    )

    assert mapped.db_payload["status"] == "partial"
    assert mapped.db_payload["total"] is None
    assert mapped.db_payload["currency"] == ""
    assert "Missing one or more key fields" in (mapped.db_payload["error"] or "")


def test_mapper_handles_invalid_json_output() -> None:
    mapped = map_hf_row_to_invoice_record(
        row={
            "instruction": "Extract invoice details into JSON.",
            "input": "Bad output",
            "output": "{bad-json}",
        },
        invoice_id="HF-42-0004",
        model_name="hf-invoice-dataset-v2",
    )

    assert mapped.db_payload["status"] == "partial"
    assert "Dataset output is not valid JSON." in (mapped.db_payload["error"] or "")
