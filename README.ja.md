# ambientdata-mcp

[English](README.md) | 日本語

[Ambient](https://ambidata.io/) の取得を行うための **MCP (Model Context Protocol) サーバー** です。
MCP クライアントから `get_data` ツールを呼び出し、Ambient の最新値や指定期間のデータを取得できます。

> 参考: Ambient API v2 を利用しています。

## クイックスタート

PyPI へは未公開のため、`uvx` に Git リポジトリを指定して起動します。

```sh
uvx git+https://github.com/hrfmtzk/ambientdata-mcp
```

## MCP クライアント設定例

主要な MCP クライアントの設定例です。`command` は `uvx`、`args` には Git リポジトリを指定します。

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

## 必要な準備

Ambient の以下の情報を用意してください。

- **Channel ID**
- **Read Key**

## 提供ツール

### `get_data`

Ambient のデータ取得を行います。以下のいずれかの指定方法を使用してください。

- **期間指定**: `from` と `to`
- **最新指定**: `n` と `skip`（`skip` は任意）

#### 入力パラメータ

| 名前         | 型                | 必須     | 説明                                         |
| ------------ | ----------------- | -------- | -------------------------------------------- |
| `read_key`   | string            | ✅       | Ambient Read Key                             |
| `channel_id` | number            | ✅       | 対象の Channel ID                            |
| `from`       | string (RFC 3339) | 条件付き | 取得開始時刻（`to` とセット）                |
| `to`         | string (RFC 3339) | 条件付き | 取得終了時刻（`from` とセット）              |
| `n`          | number            | 条件付き | 最新の取得件数（1〜1,095,000）               |
| `skip`       | number            | 任意     | 取得スキップ件数（`n` 指定時のみ）           |
| `fields`     | string[]          | 任意     | 取得するフィールド名（省略時は全フィールド） |

> `from/to` と `n/skip` は同時に指定できません。

#### 例: 期間指定

```json
{
  "read_key": "YOUR_READ_KEY",
  "channel_id": 12345,
  "from": "2024-01-01T00:00:00Z",
  "to": "2024-01-02T00:00:00Z"
}
```

#### 例: 最新の N 件取得

```json
{
  "read_key": "YOUR_READ_KEY",
  "channel_id": 12345,
  "n": 10,
  "skip": 0
}
```

#### 出力

成功時は `field_labels` と `items` を返します。

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

#### エラー

失敗時は以下の形式で返ります。

```json
{
  "category": "validation",
  "message": "Human-readable error message"
}
```

`category` は以下のいずれかになります。

- `validation`
- `forbidden`
- `not_found`
- `rate_limited`
- `upstream`

---

## 開発者向け

### セットアップ

```sh
poetry install
```

### テスト

```sh
poetry run pytest
```

### 静的解析 / フォーマット

```sh
poetry run ruff check src tests
poetry run black src tests
poetry run isort src tests
poetry run mypy src tests
```
