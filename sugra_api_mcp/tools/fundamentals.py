"""Company fundamentals tools: overview, filings, income/balance/cashflow."""

from __future__ import annotations

from typing import Any, Literal

from ..server import READ_ONLY_TOOL, get_client, mcp


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_company_overview(ticker: str) -> dict[str, Any]:
    """Get key financial metrics overview for a publicly-traded company.

    Returns market cap, P/E ratio, revenue, margins, dividend yield, and other
    headline metrics sourced from SEC EDGAR filings and market data.

    Args:
        ticker: US stock ticker symbol (uppercase). Examples: "AAPL", "MSFT", "GOOGL".

    Examples:
        get_company_overview(ticker="AAPL")
    """
    client = get_client()
    return await client.get(f"/api/v1/fundamentals/{ticker.upper()}/overview")


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_company_filings(
    ticker: str,
    jurisdiction: Literal["us", "jp"] = "us",
    statement: Literal["income", "balance", "cashflow"] | None = None,
) -> dict[str, Any]:
    """Get regulatory filings or financial statements for a company.

    For US companies, pulls from SEC EDGAR (10-K, 10-Q, 8-K).
    For Japanese companies, pulls from EDINET (annual and quarterly reports).

    Args:
        ticker: Company ticker. For US use SEC ticker ("AAPL"). For Japan use EDINET
            ticker or 4-digit code ("7203" for Toyota).
        jurisdiction: "us" for SEC EDGAR, "jp" for EDINET. Default "us".
        statement: Optional - fetch a specific statement instead of filings list.
            "income" (income statement), "balance" (balance sheet), "cashflow".

    Examples:
        get_company_filings(ticker="AAPL", statement="income")
        get_company_filings(ticker="7203", jurisdiction="jp")
    """
    client = get_client()
    if jurisdiction == "jp":
        return await client.get(f"/api/v1/edinet/{ticker}/filings")
    if statement == "income":
        return await client.get(f"/api/v1/fundamentals/{ticker.upper()}/income")
    if statement == "balance":
        return await client.get(f"/api/v1/fundamentals/{ticker.upper()}/balance")
    if statement == "cashflow":
        return await client.get(f"/api/v1/fundamentals/{ticker.upper()}/cashflow")
    return await client.get(f"/api/v1/fundamentals/{ticker.upper()}/profile")
