from __future__ import annotations

from ambientdata_mcp.client import ApiResponse
from ambientdata_mcp.models import DataItem, FieldLabels, GetDataErrorOutput, Number


def build_error_output(
    props_response: ApiResponse,
    data_response: ApiResponse,
) -> GetDataErrorOutput | None:
    for response in (props_response, data_response):
        if response.status_code < 400:
            continue

        category = _map_error_category(response.status_code)
        message = _format_error_message(response)
        return GetDataErrorOutput(category=category, message=message)

    return None


def map_error_category(status_code: int) -> str:
    return _map_error_category(status_code)


def build_data_item(payload: dict[str, object]) -> DataItem:
    created = payload.get("created")
    if not isinstance(created, str):
        raise ValueError("Ambient API response item is missing created.")

    def _as_number(value: object) -> Number | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        raise ValueError("Ambient API response item has invalid numeric value.")

    return DataItem(
        created=created,
        d1=_as_number(payload.get("d1")),
        d2=_as_number(payload.get("d2")),
        d3=_as_number(payload.get("d3")),
        d4=_as_number(payload.get("d4")),
        d5=_as_number(payload.get("d5")),
        d6=_as_number(payload.get("d6")),
        d7=_as_number(payload.get("d7")),
        d8=_as_number(payload.get("d8")),
    )


def extract_field_labels(payload: dict[str, object]) -> FieldLabels:
    def _extract_name(value: object) -> str | None:
        if isinstance(value, dict):
            name = value.get("name")
            if isinstance(name, str):
                return name
        return None

    return FieldLabels(
        d1=_extract_name(payload.get("d1")),
        d2=_extract_name(payload.get("d2")),
        d3=_extract_name(payload.get("d3")),
        d4=_extract_name(payload.get("d4")),
        d5=_extract_name(payload.get("d5")),
        d6=_extract_name(payload.get("d6")),
        d7=_extract_name(payload.get("d7")),
        d8=_extract_name(payload.get("d8")),
    )


def _map_error_category(status_code: int) -> str:
    if status_code == 403:
        return "forbidden"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "upstream"
    return "validation"


def _format_error_message(response: ApiResponse) -> str:
    if response.payload:
        if isinstance(response.payload, dict):
            message = response.payload.get("message")
            if message:
                return str(message)
    if response.raw_body:
        return response.raw_body
    return f"Ambient API error (status={response.status_code})."
