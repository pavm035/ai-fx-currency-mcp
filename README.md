# FX Currency MCP Server

A Model Context Protocol (MCP) server that provides real-time and historical foreign exchange rate data from the [Frankfurter API](https://www.frankfurter.app/). Built with FastMCP and includes GitHub OAuth authentication.

## Features

- 🌍 **31+ Currencies** - Support for major world currencies
- 💱 **Currency Conversion** - Convert between any supported currencies
- 📊 **Current Rates** - Get today's exchange rates for any base currency
- 📅 **Historical Data** - Access historical rates from 2020 onwards
- 📈 **Time Series** - Query rate changes over custom date ranges
- 🔐 **GitHub OAuth** - Secure authentication with GitHub
- 📝 **Comprehensive Logging** - Built-in logging for debugging and monitoring

## Supported Currencies

AUD, BGN, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, ISK, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PLN, RON, SEK, SGD, THB, TRY, USD, ZAR

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-fx-mcp.git
   cd ai-fx-mcp
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or with pip
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your GitHub OAuth credentials:
   ```env
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   AUTH_BASE_URL=http://localhost:8080
   ```

### GitHub OAuth Setup

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL to: `http://localhost:8080/oauth/callback`
4. Copy the Client ID and generate a Client Secret
5. Add them to your `.env` file

## Usage

### Run as HTTP Server (Development)

```bash
uv run python fx_mcp_server.py
```

Server will start on `http://localhost:8080/mcp`

### Run with Claude Desktop (stdio mode)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "fx-currency": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ai-fx-mcp",
        "run",
        "python",
        "fx_mcp_server.py",
        "--stdio"
      ],
      "env": {
        "GITHUB_CLIENT_ID": "your_github_client_id",
        "GITHUB_CLIENT_SECRET": "your_github_client_secret",
        "AUTH_BASE_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Available Tools

### `available_currencies()`
Returns a list of all supported currency codes and names.

**Example Response:**
```json
{
  "USD": "United States Dollar",
  "EUR": "Euro",
  "JPY": "Japanese Yen"
}
```

### `convert_currency(from_code: str, to_code: str, amount: float = 1.0)`
Convert an amount from one currency to another.

**Parameters:**
- `from_code`: Source currency code (e.g., "USD")
- `to_code`: Target currency code (e.g., "EUR")
- `amount`: Amount to convert (default: 1.0)

**Example:**
```python
convert_currency("USD", "EUR", 100)
# Returns: {"amount": 100, "base": "USD", "rates": {"EUR": 0.85}, "converted_amount": 85.0}
```

### `today_rates(code: str)`
Get current exchange rates for a base currency.

**Parameters:**
- `code`: Base currency code (e.g., "USD")

**Example:**
```python
today_rates("USD")
# Returns all current rates relative to USD
```

### `historical_rates(date: str, base: str = "EUR", symbols: str | None = None)`
Get exchange rates for a specific historical date.

**Parameters:**
- `date`: Date in YYYY-MM-DD format
- `base`: Base currency code (default: "EUR")
- `symbols`: Optional comma-separated currency codes to filter

**Example:**
```python
historical_rates("2024-01-15", "USD", "EUR,JPY")
```

### `time_series_rates(start_date: str, end_date: str, base: str = "EUR", symbols: str | None = None)`
Get exchange rate time series data over a date range.

**Parameters:**
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format
- `base`: Base currency code (default: "EUR")
- `symbols`: Optional comma-separated currency codes to filter

**Example:**
```python
time_series_rates("2024-01-01", "2024-01-31", "USD", "EUR,JPY")
```

## Logging

Logs are written to:
- **Console** (stdout) - captured by cloud platforms
- **File** (`/tmp/fx-mcp-server.log`) - for local development

View logs in real-time:
```bash
tail -f /tmp/fx-mcp-server.log
```

Filter for application logs only:
```bash
tail -f /tmp/fx-mcp-server.log | grep __main__
```

## Deployment

The server is cloud-ready with stdout logging that works with:
- AWS ECS/Fargate (CloudWatch Logs)
- Google Cloud Run (Cloud Logging)
- Azure Container Apps (Azure Monitor)
- Any container platform

## Development

### Project Structure

```
ai-fx-mcp/
├── fx_mcp_server.py    # Main MCP server implementation
├── pyproject.toml      # Project dependencies and metadata
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

### Testing

Test individual tools:
```bash
uv run python -c "from fx_mcp_server import convert_currency; print(convert_currency('USD', 'EUR', 100))"
```

## Data Source

Exchange rate data is provided by [Frankfurter API](https://www.frankfurter.app/), a free and open-source API for current and historical foreign exchange rates published by the European Central Bank.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Pavan

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Frankfurter API](https://www.frankfurter.app/) - Currency data provider
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification