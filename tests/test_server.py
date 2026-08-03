from typing import cast

import pytest
from click.testing import CliRunner
from mcp.server.mcpserver import Context
from pytest_mock import MockFixture

from ambient_mcp.client import ApiResponse
from ambient_mcp.models import GetDataErrorOutput, GetDataInput, GetDataOutput
from ambient_mcp.server import get_data, main, mcp


class DummyContext:
    async def info(self, _: str) -> None:
        return None

    async def debug(self, _: str) -> None:
        return None

    async def error(self, _: str) -> None:
        return None


def _dummy_context() -> Context[None, None]:
    return cast(Context[None, None], DummyContext())


@pytest.mark.asyncio
async def test_get_data_returns_error_output(mocker: MockFixture) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = _dummy_context()

    mocker.patch(
        "ambient_mcp.server.AmbientClient.get_channel_properties",
        return_value=ApiResponse(status_code=200, payload={}, raw_body=""),
    )
    mocker.patch(
        "ambient_mcp.server.AmbientClient.get_data",
        return_value=ApiResponse(status_code=500, payload={}, raw_body=""),
    )
    mocker.patch(
        "ambient_mcp.server.build_error_output",
        return_value=GetDataErrorOutput(category="upstream", message="boom"),
    )

    result = await get_data(params, context)

    assert isinstance(result, GetDataErrorOutput)
    assert result.category == "upstream"
    assert result.message == "boom"


@pytest.mark.asyncio
async def test_get_data_returns_success_output(mocker: MockFixture) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = _dummy_context()

    mocker.patch(
        "ambient_mcp.server.AmbientClient.get_channel_properties",
        return_value=ApiResponse(
            status_code=200,
            payload={"d1": {"name": "temperature"}},
            raw_body="",
        ),
    )
    mocker.patch(
        "ambient_mcp.server.AmbientClient.get_data",
        return_value=ApiResponse(
            status_code=200,
            payload=[{"created": "2024-01-01T00:00:00Z", "d1": 1}],
            raw_body="",
        ),
    )
    mocker.patch("ambient_mcp.server.build_error_output", return_value=None)

    result = await get_data(params, context)

    assert isinstance(result, GetDataOutput)
    assert result.field_labels.d1 == "temperature"
    assert result.items[0].d1 == 1


@pytest.mark.asyncio
async def test_get_data_returns_validation_error_on_exception(
    mocker: MockFixture,
) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = _dummy_context()

    mocker.patch(
        "ambient_mcp.server.AmbientClient.get_channel_properties",
        side_effect=RuntimeError("broken"),
    )

    result = await get_data(params, context)

    assert isinstance(result, GetDataErrorOutput)
    assert result.category == "validation"
    assert "broken" in result.message


class TestMain:
    def test_defaults(self, mocker: MockFixture) -> None:
        mock_run = mocker.patch.object(mcp, "run")
        result = CliRunner().invoke(main, [])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(transport="stdio")

    def test_cli_args(self, mocker: MockFixture) -> None:
        mock_run = mocker.patch.object(mcp, "run")
        result = CliRunner().invoke(
            main,
            ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"],
        )
        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            transport="streamable-http", host="0.0.0.0", port=9000
        )

    def test_env_vars(self, mocker: MockFixture) -> None:
        mock_run = mocker.patch.object(mcp, "run")
        result = CliRunner().invoke(
            main,
            [],
            env={"MCP_TRANSPORT": "sse", "MCP_HOST": "0.0.0.0", "MCP_PORT": "9000"},
        )
        assert result.exit_code == 0
        mock_run.assert_called_once_with(transport="sse", host="0.0.0.0", port=9000)

    def test_invalid_transport(self) -> None:
        result = CliRunner().invoke(main, ["--transport", "invalid"])
        assert result.exit_code != 0
