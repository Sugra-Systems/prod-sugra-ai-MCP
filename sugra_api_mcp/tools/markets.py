"""Market data tools: prices, history, overview, symbol lookup, prediction markets."""

from __future__ import annotations

from typing import Any, Literal

from ..server import READ_ONLY_TOOL, get_client, mcp

AssetType = Literal["stock", "crypto", "forex", "commodity"]


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_market_price(
    symbol: str,
    asset_type: AssetType = "stock",
    vs_currency: str = "usd",
) -> dict[str, Any]:
    """Get the current market price for a stock, cryptocurrency, forex pair, or commodity.

    Returns the latest price in a normalized envelope: `{data: {...}, meta: {source, data_time, ...}}`.

    Args:
        symbol: Asset identifier. Lowercase slug for crypto ("bitcoin", "ethereum"),
            uppercase ticker for stocks ("AAPL", "MSFT"), ISO 4217 pair for forex
            ("EURUSD", "USDJPY"), or commodity slug ("gold", "oil", "wheat").
        asset_type: One of "stock", "crypto", "forex", "commodity". Default "stock".
        vs_currency: Quote currency for crypto/commodity. ISO 4217 lowercase (e.g. "usd", "eur").
            Ignored for stocks and forex. Default "usd".

    Examples:
        get_market_price(symbol="bitcoin", asset_type="crypto")
        get_market_price(symbol="AAPL", asset_type="stock")
        get_market_price(symbol="EURUSD", asset_type="forex")
        get_market_price(symbol="gold", asset_type="commodity")
    """
    client = get_client()
    if asset_type == "crypto":
        return await client.get(
            f"/api/v1/crypto/{symbol.lower()}/price",
            params={"vs_currency": vs_currency.lower()},
        )
    if asset_type == "stock":
        return await client.get(f"/api/v2/quotes/{symbol.upper()}/price")
    if asset_type == "forex":
        base, quote = symbol[:3].upper(), symbol[3:].upper()
        return await client.get(
            "/api/v1/forex/convert",
            params={"from": base, "to": quote, "amount": 1},
        )
    if asset_type == "commodity":
        return await client.get(
            f"/api/v1/commodities/{symbol.lower()}/price",
            params={"vs_currency": vs_currency.lower()},
        )
    return {"error": f"Unknown asset_type: {asset_type}"}


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_historical_prices(
    symbol: str,
    asset_type: AssetType = "stock",
    period: str = "1mo",
    interval: str = "1d",
) -> dict[str, Any]:
    """Get historical OHLCV time series for a tradable asset.

    Returns a list of price bars with open, high, low, close, and volume.

    Args:
        symbol: Asset identifier (see get_market_price for formats).
        asset_type: One of "stock", "crypto", "forex", "commodity". Default "stock".
        period: Lookback range. Common values: "1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max".
        interval: Bar size. Common values: "1m", "5m", "15m", "1h", "1d", "1wk", "1mo".

    Examples:
        get_historical_prices(symbol="AAPL", period="1y", interval="1d")
        get_historical_prices(symbol="bitcoin", asset_type="crypto", period="3mo")
    """
    client = get_client()
    if asset_type == "stock":
        return await client.get(
            f"/api/v2/quotes/{symbol.upper()}/historical",
            params={"range": period, "interval": interval},
        )
    if asset_type == "crypto":
        return await client.get(
            f"/api/v1/crypto/{symbol.lower()}/history",
            params={"days": _period_to_days(period)},
        )
    if asset_type == "forex":
        base, quote = symbol[:3].upper(), symbol[3:].upper()
        return await client.get(
            "/api/v1/forex/history",
            params={"base": base, "quote": quote, "period": period},
        )
    if asset_type == "commodity":
        return await client.get(
            f"/api/v1/commodities/{symbol.lower()}/history",
            params={"period": period},
        )
    return {"error": f"Unknown asset_type: {asset_type}"}


@mcp.tool(annotations=READ_ONLY_TOOL)
async def search_symbol(query: str, asset_type: AssetType | None = None) -> dict[str, Any]:
    """Find a ticker or symbol by company name, description, or free-text query.

    Returns candidate symbols with name, exchange, and asset type.

    Use before get_market_price when you only know the company name, not the ticker.

    Args:
        query: Search string. Examples: "apple", "tesla motors", "bitcoin", "euro to dollar".
        asset_type: Optional filter. If omitted, searches across all asset classes.

    Examples:
        search_symbol(query="apple")
        search_symbol(query="nvidia", asset_type="stock")
        search_symbol(query="ether", asset_type="crypto")
    """
    client = get_client()
    if asset_type == "crypto":
        return await client.get("/api/v1/crypto/search", params={"q": query})
    if asset_type == "stock" or asset_type is None:
        return await client.get("/api/v2/market/search", params={"q": query})
    if asset_type == "forex":
        return await client.get("/api/v1/forex/currencies", params={"q": query})
    return {"error": f"search_symbol does not support asset_type={asset_type}"}


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_market_overview(asset_type: Literal["stock", "crypto"] = "crypto") -> dict[str, Any]:
    """Get a market snapshot: top movers, total market cap, sector performance.

    Args:
        asset_type: "crypto" for global crypto markets, "stock" for US equity overview.

    Examples:
        get_market_overview(asset_type="crypto")
        get_market_overview(asset_type="stock")
    """
    client = get_client()
    if asset_type == "crypto":
        return await client.get("/api/v1/crypto/market/global")
    return await client.get("/api/v2/market/overview")


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_prediction_market(
    query: str | None = None,
    event_ticker: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Get prediction market contracts from Kalshi (CFTC-regulated exchange).

    Returns event-level markets with yes/no prices, volume, and close dates.

    Args:
        query: Optional free-text filter to narrow events (e.g. "election", "inflation").
        event_ticker: Optional specific event ticker for detailed view.
        limit: Maximum number of events to return. Default 20.

    Examples:
        get_prediction_market(query="fed rate")
        get_prediction_market(event_ticker="PRES-2028")
    """
    client = get_client()
    if event_ticker:
        return await client.get(f"/api/v1/kalshi/events/{event_ticker}")
    return await client.get("/api/v1/kalshi/events", params={"q": query, "limit": limit})


def _period_to_days(period: str) -> int:
    mapping = {
        "1d": 1, "5d": 5, "1w": 7,
        "1mo": 30, "3mo": 90, "6mo": 180,
        "1y": 365, "2y": 730, "5y": 1825, "max": 3650,
    }
    return mapping.get(period, 30)
