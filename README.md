# ambientdata-mcp

English | [日本語](README.ja.md)

This is an **MCP (Model Context Protocol) server** for retrieving data from [Ambient](https://ambidata.io/).
You can call the `get_data` tool from your MCP client to fetch the latest values or data within a time range.

> Note: This server uses the Ambient API v2.

## Quick Start

The package is not yet published on PyPI, so run it via `uvx` with the Git repository.

```sh
uvx git+https://github.com/hrfmtzk/ambientdata-mcp
```

## MCP Client Configuration Example

Below is a typical MCP client configuration. Use `uvx` as the command and pass the Git repository in `args`.

```json
{
  "mcpServers": {
    "ambientdata": {
      "command": "uvx",
      "args": ["git+https://github.com/hrfmtzk/ambientdata-mcp"]
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
poetry install
```

### Tests

```sh
poetry run pytest
```

### Lint / Format

```sh
poetry run ruff check src tests
poetry run black src tests
poetry run isort src tests
poetry run mypy src tests
```
