import asyncio

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from ambient_mcp.client import AmbientClient
from ambient_mcp.models import (
    GetDataErrorOutput,
    GetDataInput,
    GetDataOutput,
    GetDataResult,
)
from ambient_mcp.transformers import (
    build_data_item,
    build_error_output,
    extract_field_labels,
)

mcp = FastMCP("ambient-mcp")


@mcp.tool(name="get_data")
async def get_data(
    params: GetDataInput,
    ctx: Context[ServerSession, None],
) -> GetDataResult:
    """Retrieve Ambient items by time range or latest count."""
    await ctx.info(f"get_data called with {params}")

    try:
        client = AmbientClient(
            channel_id=params.channel_id,
            read_key=params.read_key,
        )
        props_response, data_response = await asyncio.gather(
            client.get_channel_properties(),
            client.get_data(
                from_=params.from_,
                to=params.to,
                n=params.n,
                skip=params.skip,
            ),
        )

        await ctx.debug(f"props_response: {props_response}")
        await ctx.debug(f"data_response: {data_response}")

        error_output = build_error_output(props_response, data_response)
        if error_output:
            return error_output

        props_payload = props_response.payload or {}
        if not isinstance(props_payload, dict):
            raise ValueError("Ambient API properties payload is invalid.")

        data_payload_raw = data_response.payload or []
        if not isinstance(data_payload_raw, list):
            raise ValueError("Ambient API response body is not a list.")
        if not all(isinstance(item, dict) for item in data_payload_raw):
            raise ValueError("Ambient API response items are invalid.")
        data_payload = data_payload_raw

        return GetDataOutput(
            field_labels=extract_field_labels(props_payload),
            items=[build_data_item(item) for item in data_payload],
        )
    except Exception as exc:
        await ctx.error(f"get_data error: {exc}")
        return GetDataErrorOutput(
            category="validation",
            message=str(exc),
        )


def main() -> None:
    mcp.run()
