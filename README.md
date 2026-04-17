# sugra-api-mcp

[![PyPI](https://img.shields.io/pypi/v/sugra-api-mcp.svg)](https://pypi.org/project/sugra-api-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/sugra-api-mcp.svg)](https://pypi.org/project/sugra-api-mcp/)
[![License](https://img.shields.io/pypi/l/sugra-api-mcp.svg)](https://github.com/Sugra-Systems/prod-sugra-ai-MCP/blob/main/LICENSE)

Official [Model Context Protocol](https://modelcontextprotocol.io) server for the [Sugra API](https://sugra.ai) - unified access to 518+ intelligence endpoints spanning financial markets, macroeconomics, fundamentals, government data, physical world signals, and news.

Use it from Claude Desktop, Cursor, Zed, Cline, claude.ai, or any MCP-compatible agent.

## What you get

17 tools covering the full Sugra API:

| Category | Tools |
|---|---|
| Markets | `get_market_price`, `get_historical_prices`, `get_market_overview`, `search_symbol`, `get_prediction_market` |
| Fundamentals | `get_company_overview`, `get_company_filings` |
| Macro | `get_macro_indicator`, `get_central_bank_rate`, `search_economic_series` |
| Government | `get_government_spending`, `get_treasury_data` |
| Physical world | `get_weather`, `get_environmental_data` |
| News | `get_news` |
| Discovery | `search_endpoint`, `call_endpoint` (covers all 518 endpoints) |

## Installation

```bash
pip install sugra-api-mcp
```

Get a free API key at [app.sugra.ai/settings/billing](https://app.sugra.ai/settings/billing) (Free tier: 50 req/day).

## Usage with Claude Desktop (stdio)

Add to `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sugra": {
      "command": "python",
      "args": ["-m", "sugra_api_mcp"],
      "env": {
        "SUGRA_API_KEY": "sugra_xxx_yourkey..."
      }
    }
  }
}
```

Restart Claude Desktop. Sugra tools appear in the tools menu.

## Usage with Cursor, Zed, Cline

Same stdio config as above, in the respective MCP settings file.

## Usage over HTTP (claude.ai, remote agents)

If you prefer not to install anything locally, use the hosted Streamable HTTP endpoint:

```
https://app.sugra.ai/mcp
```

Add to claude.ai or any Streamable HTTP MCP client with `Authorization: Bearer sugra_xxx_...` header.

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SUGRA_API_KEY` | Yes | - | Your Sugra API key |
| `SUGRA_API_BASE` | No | `https://sugra.ai` | Override for self-hosted or beta environments |
| `SUGRA_TIMEOUT` | No | `30` | Request timeout in seconds |

## Examples

Ask Claude:

- "What's Bitcoin's current price and how did it move this week?"
- "Show me Apple's income statement and debt profile."
- "Compare US vs Germany CPI over the last 5 years."
- "What's the Fed funds rate today, and what was the last change?"
- "Find all Sugra endpoints related to shipping or vessels."

## Development

```bash
git clone https://github.com/Sugra-Systems/prod-sugra-ai-MCP
cd prod-sugra-ai-MCP
pip install -e ".[dev,http]"
export SUGRA_API_KEY=sugra_...
python -m sugra_api_mcp  # stdio mode
python -m sugra_api_mcp --transport streamable-http --port 8001  # HTTP mode
```

Run tests:

```bash
pytest
```

## License

MIT © Sugra Systems, Inc.
