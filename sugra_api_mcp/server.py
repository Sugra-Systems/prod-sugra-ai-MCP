"""FastMCP server instance and shared client accessor."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .client import SugraClient
from .config import load_config

mcp = FastMCP(
    "sugra-api",
    instructions=(
        "Sugra API - unified data access across 518+ endpoints: financial markets, "
        "macroeconomics, fundamentals, government data, physical world, and news. "
        "Use curated tools (get_market_price, get_macro_indicator, etc.) when they "
        "match the task. Fall back to search_endpoint + call_endpoint for broader coverage."
    ),
)

_client: SugraClient | None = None


def get_client() -> SugraClient:
    """Lazily instantiate the Sugra HTTP client.

    We avoid creating the client at import time so the process can start
    even if SUGRA_API_KEY is missing (e.g. during `--help`).
    """
    global _client
    if _client is None:
        _client = SugraClient(load_config())
    return _client
