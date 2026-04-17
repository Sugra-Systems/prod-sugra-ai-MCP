"""Macroeconomic data tools: GDP, CPI, central bank rates, search."""

from __future__ import annotations

from typing import Any, Literal

from ..server import get_client, mcp

CentralBank = Literal["fed", "ecb", "boj", "boe", "snb", "pboc", "rba", "boc"]


@mcp.tool()
async def get_macro_indicator(
    country: str,
    section: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Get a macroeconomic time series for a country.

    Returns a time series for the requested indicator, aggregated from primary sources
    (FRED, BIS, BOJ, BoE, StatCan, ABS, Eurostat, Destatis, and others).

    Args:
        country: Country code. Use lowercase 2-letter ISO codes ("us", "de", "jp", "uk",
            "ca", "au", "ch") or "eu" for Eurozone aggregate.
        section: Indicator category. Common values: "gdp", "cpi", "unemployment",
            "interest-rate", "trade", "industrial-production", "retail-sales", "pmi".
        start_date: Optional start date in YYYY-MM-DD format.
        end_date: Optional end date in YYYY-MM-DD format.

    Examples:
        get_macro_indicator(country="us", section="cpi")
        get_macro_indicator(country="de", section="gdp", start_date="2020-01-01")
    """
    client = get_client()
    return await client.get(
        f"/api/v1/macro/{country.lower()}/{section.lower()}",
        params={"start_date": start_date, "end_date": end_date},
    )


@mcp.tool()
async def get_central_bank_rate(
    bank: CentralBank = "fed",
    rate_type: str | None = None,
) -> dict[str, Any]:
    """Get current and historical policy rate for a major central bank.

    Args:
        bank: Central bank code. "fed" (US Federal Reserve), "ecb" (European Central Bank),
            "boj" (Bank of Japan), "boe" (Bank of England), "snb" (Swiss National Bank),
            "pboc" (People's Bank of China), "rba" (Reserve Bank of Australia),
            "boc" (Bank of Canada). Default "fed".
        rate_type: Optional specific rate type (e.g. "effr" for effective federal funds
            rate, "sofr" for secured overnight financing rate). If omitted, returns
            the headline policy rate.

    Examples:
        get_central_bank_rate(bank="fed")
        get_central_bank_rate(bank="fed", rate_type="sofr")
        get_central_bank_rate(bank="ecb")
    """
    client = get_client()
    if bank == "fed":
        if rate_type:
            return await client.get(f"/api/v1/fed/rates/{rate_type.lower()}")
        return await client.get("/api/v1/fed/rates")
    # Other banks mapped via macro interest-rate section
    country_map = {
        "ecb": "eu", "boj": "jp", "boe": "uk", "snb": "ch",
        "pboc": "cn", "rba": "au", "boc": "ca",
    }
    return await client.get(f"/api/v1/macro/{country_map[bank]}/interest-rate")


@mcp.tool()
async def search_economic_series(
    query: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Search across all economic data series catalogs (FRED, BIS, BOJ, BoE, Eurostat).

    Use this to discover what indicators are available when you don't know the exact
    country/section combination for get_macro_indicator.

    Args:
        query: Free-text search query.
        limit: Maximum number of results to return. Default 20.

    Examples:
        search_economic_series(query="inflation breakeven")
        search_economic_series(query="chinese export prices")
    """
    client = get_client()
    return await client.get("/api/v1/macro/search", params={"q": query, "limit": limit})
