import pytest

from ambient_mcp.client import ApiResponse
from ambient_mcp.transformers import (
    build_data_item,
    build_error_output,
    extract_field_labels,
    map_error_category,
)


def test_build_data_item_accepts_numeric_and_none() -> None:
    item = build_data_item(
        {
            "created": "2024-01-01T00:00:00Z",
            "d1": 1,
            "d2": 1.5,
            "d3": None,
        }
    )
    assert item.created == "2024-01-01T00:00:00Z"
    assert item.d1 == 1
    assert item.d2 == 1.5
    assert item.d3 is None


def test_build_data_item_requires_created() -> None:
    with pytest.raises(TypeError, match="missing created"):
        build_data_item({"d1": 1})


def test_build_data_item_rejects_invalid_number() -> None:
    with pytest.raises(ValueError, match="invalid numeric value"):
        build_data_item({"created": "2024-01-01T00:00:00Z", "d1": "nope"})


def test_extract_field_labels_picks_name_values() -> None:
    labels = extract_field_labels(
        {
            "d1": {"name": "temperature"},
            "d2": {"name": "humidity"},
            "d3": {"label": "ignored"},
        }
    )
    assert labels.d1 == "temperature"
    assert labels.d2 == "humidity"
    assert labels.d3 is None


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (403, "forbidden"),
        (404, "not_found"),
        (429, "rate_limited"),
        (500, "upstream"),
        (422, "validation"),
    ],
)
def test_map_error_category(status: int, expected: str) -> None:
    assert map_error_category(status) == expected


def test_build_error_output_prefers_error_responses() -> None:
    ok = ApiResponse(status_code=200, payload=None, raw_body="")
    error = ApiResponse(status_code=404, payload={"message": "missing"}, raw_body="")
    output = build_error_output(ok, error)
    assert output is not None
    assert output.category == "not_found"
    assert output.message == "missing"


def test_build_error_output_returns_none_when_all_ok() -> None:
    ok = ApiResponse(status_code=200, payload=None, raw_body="")
    assert build_error_output(ok, ok) is None
