"""FastMCP server instance and shared client accessor."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .client import SugraClient
from .config import load_config


def _build_transport_security() -> TransportSecuritySettings | None:
    """Build DNS rebinding protection settings from SUGRA_MCP_ALLOWED_HOSTS.

    When deployed behind a reverse proxy (e.g. nginx at app.sugra.ai), the Host
    header won't match the default localhost allowlist. Set the env var to a
    comma-separated list of public hostnames to allow.
    """
    raw = os.environ.get("SUGRA_MCP_ALLOWED_HOSTS", "").strip()
    if not raw:
        return None
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[*hosts, "127.0.0.1:*", "localhost:*", "[::1]:*"],
        allowed_origins=[
            *[f"https://{h}" for h in hosts],
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://[::1]:*",
        ],
    )


mcp = FastMCP(
    "sugra-api",
    instructions=(
        "Sugra API - unified data access across 518+ endpoints: financial markets, "
        "macroeconomics, fundamentals, government data, physical world, and news. "
        "Use curated tools (get_market_price, get_macro_indicator, etc.) when they "
        "match the task. Fall back to search_endpoint + call_endpoint for broader coverage."
    ),
    transport_security=_build_transport_security(),
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
