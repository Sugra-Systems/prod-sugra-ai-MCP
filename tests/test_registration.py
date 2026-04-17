"""Sanity tests: tools import and register correctly."""

from __future__ import annotations

import os


def test_tools_register(monkeypatch):
    monkeypatch.setenv("SUGRA_API_KEY", "dummy")
    from sugra_api_mcp import tools  # noqa: F401
    from sugra_api_mcp.server import mcp

    import asyncio
    tool_list = asyncio.run(mcp.list_tools())
    assert len(tool_list) == 17
    names = {t.name for t in tool_list}
    expected = {
        "get_market_price", "get_historical_prices", "search_symbol",
        "get_market_overview", "get_prediction_market",
        "get_company_overview", "get_company_filings",
        "get_macro_indicator", "get_central_bank_rate", "search_economic_series",
        "get_government_spending", "get_treasury_data",
        "get_weather", "get_environmental_data",
        "get_news",
        "search_endpoint", "call_endpoint",
    }
    assert names == expected, f"Mismatch: missing={expected - names}, extra={names - expected}"


def test_config_requires_api_key(monkeypatch):
    monkeypatch.delenv("SUGRA_API_KEY", raising=False)
    from sugra_api_mcp.config import load_config
    import pytest
    with pytest.raises(RuntimeError, match="SUGRA_API_KEY"):
        load_config()


def test_config_defaults(monkeypatch):
    monkeypatch.setenv("SUGRA_API_KEY", "sugra_test_123")
    monkeypatch.delenv("SUGRA_API_BASE", raising=False)
    monkeypatch.delenv("SUGRA_TIMEOUT", raising=False)
    from sugra_api_mcp.config import load_config
    cfg = load_config()
    assert cfg.api_key == "sugra_test_123"
    assert cfg.api_base == "https://sugra.ai"
    assert cfg.timeout == 30.0
