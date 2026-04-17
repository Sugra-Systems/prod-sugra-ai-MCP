"""Async HTTP client for the Sugra API."""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config


class SugraClient:
    """Thin async wrapper over the Sugra API with x-api-key auth."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.api_base,
            headers={
                "x-api-key": config.api_key,
                "User-Agent": "sugra-api-mcp/0.1.0",
                "Accept": "application/json",
            },
            timeout=config.timeout,
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        response = await self._client.get(path, params=clean_params)
        return self._handle(response)

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        response = await self._client.post(path, json=json or {})
        return self._handle(response)

    @staticmethod
    def _handle(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            payload = {"error": response.text[:500]}
        if response.status_code >= 400:
            error = payload.get("error") if isinstance(payload, dict) else str(payload)
            return {
                "error": error or f"HTTP {response.status_code}",
                "status_code": response.status_code,
                "url": str(response.request.url),
            }
        return payload

    async def aclose(self) -> None:
        await self._client.aclose()
