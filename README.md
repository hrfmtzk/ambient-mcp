# ambient-mcp

English | [日本語](README.ja.md)

This is an **MCP (Model Context Protocol) server** for retrieving data from [Ambient](https://ambidata.io/).
You can call the `get_data` tool from your MCP client to fetch the latest values or data within a time range.

> Note: This server uses the Ambient API v2.

## Quick Start

The package is not yet published on PyPI, so run it via `uvx` with the Git repository.

```sh
uvx git+https://github.com/hrfmtzk/ambient-mcp
```

## Transport Configuration

Three transport protocols are available. Use `--transport` (or the `MCP_TRANSPORT` environment variable) to select one.

| Transport | Description | Default |
| --- | --- | --- |
| `stdio` | Standard I/O — for MCP clients that spawn the server as a subprocess | ✅ |
| `streamable-http` | Streamable HTTP — recommended for network-accessible servers | |
| `sse` | Server-Sent Events — legacy HTTP transport | |

For `sse` and `streamable-http`, you can also configure `--host` (env: `MCP_HOST`, default: `127.0.0.1`) and `--port` (env: `MCP_PORT`, default: `8000`).

```sh
# Start with streamable-http, bind to all interfaces
ambient-mcp --transport streamable-http --host 0.0.0.0 --port 8000

# Same using environment variables
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 ambient-mcp
```

## MCP Client Configuration Example

### stdio (subprocess)

Use `uvx` as the command and pass the Git repository in `args`.

```json
{
  "mcpServers": {
    "ambient": {
      "command": "uvx",
      "args": ["git+https://github.com/hrfmtzk/ambient-mcp"]
    }
  }
}
```

### streamable-http (network)

Start the server separately, then point your MCP client at its URL.

```json
{
  "mcpServers": {
    "ambient": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### sse (network, legacy)

```json
{
  "mcpServers": {
    "ambient": {
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

## Prerequisites

Prepare the following information from Ambient:

- **Channel ID**
- **Read Key**

## Tools

### `get_data`

Fetch Ambient items using one of the following approaches:

- **Time range**: `from` and `to`
- **Latest items**: `n` and `skip` (`skip` is optional)

#### Input Parameters

| Name         | Type              | Required    | Description                                     |
| ------------ | ----------------- | ----------- | ----------------------------------------------- |
| `read_key`   | string            | ✅          | Ambient Read Key                                |
| `channel_id` | number            | ✅          | Target Channel ID                               |
| `from`       | string (RFC 3339) | Conditional | Start time (use with `to`)                      |
| `to`         | string (RFC 3339) | Conditional | End time (use with `from`)                      |
| `n`          | number            | Conditional | Number of latest items to fetch (1–1,095,000)   |
| `skip`       | number            | Optional    | Items to skip (requires `n`)                    |
| `fields`     | string[]          | Optional    | Field names to retrieve (all fields if omitted) |

> You cannot combine `from/to` with `n/skip`.

#### Example: Time Range

```json
{
  "read_key": "YOUR_READ_KEY",
  "channel_id": 12345,
  "from": "2024-01-01T00:00:00Z",
  "to": "2024-01-02T00:00:00Z"
}
```

#### Example: Latest N Items

```json
{
  "read_key": "YOUR_READ_KEY",
  "channel_id": 12345,
  "n": 10,
  "skip": 0
}
```

#### Output

On success, the tool returns `field_labels` and `items`.

```json
{
  "field_labels": {
    "d1": "Temperature",
    "d2": "Humidity"
  },
  "items": [
    {
      "created": "2024-01-01T00:00:00Z",
      "d1": 23.4,
      "d2": 45.1
    }
  ]
}
```

#### Errors

On failure, the tool returns:

```json
{
  "category": "validation",
  "message": "Human-readable error message"
}
```

Possible `category` values:

- `validation`
- `forbidden`
- `not_found`
- `rate_limited`
- `upstream`

---

## Developer Notes

### Setup

```sh
uv sync
```

### Tests

```sh
uv run pytest
```

### Lint / Format

```sh
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src tests
```
