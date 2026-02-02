from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass(slots=True)
class ApiResponse:
    status_code: int
    payload: Optional[Any]
    raw_body: str


class AmbientApiError(RuntimeError):
    def __init__(self, message: str, response: ApiResponse):
        super().__init__(message)
        self.response = response


class AmbientClient:
    def __init__(
        self,
        channel_id: int,
        read_key: str,
        *,
        base_url: str = "https://ambidata.io/api/v2",
        timeout: float = 30.0,
    ) -> None:
        self.channel_id = channel_id
        self.read_key = read_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_channel_properties(self) -> ApiResponse:
        url = f"{self.base_url}/channels/{self.channel_id}"
        return await self._get(url, params={"readKey": self.read_key})

    async def get_data(
        self,
        *,
        from_: Optional[str],
        to: Optional[str],
        n: Optional[int],
        skip: Optional[int],
    ) -> ApiResponse:
        url = f"{self.base_url}/channels/{self.channel_id}/data"
        params: dict[str, Any] = {"readKey": self.read_key}

        if from_ is not None and to is not None:
            params["start"] = from_
            params["end"] = to
        if n is not None:
            params["n"] = n
        if skip is not None:
            params["skip"] = skip

        return await self._get(url, params=params)

    async def _get(self, url: str, *, params: dict[str, Any]) -> ApiResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

        raw_body = response.text
        payload: Optional[dict[str, Any]] = None
        if raw_body:
            try:
                payload = json.loads(raw_body)
            except json.JSONDecodeError:
                payload = None

        return ApiResponse(
            status_code=response.status_code,
            payload=payload,
            raw_body=raw_body,
        )
