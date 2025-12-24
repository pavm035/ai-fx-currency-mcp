import os
from dotenv import load_dotenv
import requests
import uvicorn
import logging

from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

load_dotenv()

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/fx-mcp-server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Optional authentication via environment variable
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"

API = "https://api.frankfurter.dev/v1"

# Setup auth if enabled
if ENABLE_AUTH:
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
    
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET or not AUTH_BASE_URL:
        raise ValueError(
            "ENABLE_AUTH=true but missing required environment variables!\n"
            "Please set:\n"
            "  - GITHUB_CLIENT_ID\n"
            "  - GITHUB_CLIENT_SECRET\n"
            "  - AUTH_BASE_URL"
        )
    
    github_auth = GitHubProvider(
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        base_url=AUTH_BASE_URL,
        required_scopes=["user:email"]
    )
    logger.info("GitHub authentication enabled")
    mcp = FastMCP("Fx Rates", auth=github_auth)
else:
    logger.info("Running without authentication")
    mcp = FastMCP("Fx Rates")

# Tools
@mcp.tool
def available_currencies() -> dict:
    """
    Provides the list of available currencies from frankfurter dev API as of today

    Raise:
        Raises an exception if API failed or so

    Returns:
        - json: JSON object with list of currency code and value(name)
    """
    logger.info("Fetching available currencies")
    try:
        currencies_api = f"{API}/currencies"
        response = requests.get(currencies_api)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Successfully fetched {len(result)} currencies")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch available currencies: {e}")
        raise e


@mcp.tool
def convert_currency(from_code: str, to_code: str, amount: float = 1.0) -> dict:
    """
    Converts the currency from one code to another code

    Args:
        - from_code: From currency code ex: (USD, EUR, INR)
        - to_code: To currency code ex: (USD, EUR, INR)
        - amount: Amount to convert (default: 1.0)

    Raise:
        Raises an exception if API failed or so

    Returns:
        - dict: Returns the conversion info including calculated amount
    """
    logger.info(f"Converting {amount} {from_code} to {to_code}")
    try:
        conversion_api = f"{API}/latest?base={from_code}&symbols={to_code}"
        response = requests.get(conversion_api)
        response.raise_for_status()
        data = response.json()
        
        # Calculate the converted amount
        if to_code in data.get("rates", {}):
            rate = data["rates"][to_code]
            converted_amount = amount * rate
            data["amount"] = amount
            data["converted_amount"] = round(converted_amount, 2)
            logger.info(f"Successfully converted: {amount} {from_code} = {converted_amount} {to_code}")
        
        return data
    except Exception as e:
        logger.error(f"Failed to convert currency: {e}")
        raise e


@mcp.tool
def today_rates(code: str) -> dict:
    """
    Retrieves the current exchange rates for the given currency code

    Args:
        - code: Base currency code ex: (USD, EUR, INR)

    Returns:
        - dict: Current rates for all currencies relative to the base currency
    """
    logger.info(f"Fetching today's rates for {code}")
    try:
        rates_api = f"{API}/latest?base={code}"
        response = requests.get(rates_api)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Successfully fetched today's rates for {code}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch rates: {e}")
        raise e


@mcp.tool
def historical_rates(date: str, base: str = "EUR", symbols: str | None = None) -> dict:
    """
    Retrieves exchange rates for a specific date

    Args:
        - date: Date in YYYY-MM-DD format (e.g., 2024-01-15)
        - base: Base currency code (default: EUR)
        - symbols: Comma-separated currency codes to filter (optional)

    Returns:
        - dict: Historical rates for the specified date
    """
    logger.info(f"Fetching historical rates date: {date} base: {base} symbols: {symbols}")
    try:
        historical_api = f"{API}/{date}?base={base}"
        if symbols:
            historical_api += f"&symbols={symbols}"
        
        response = requests.get(historical_api)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Successfully fetched historical rates for {date}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch historical rates: {e}")
        raise e


@mcp.tool
def time_series_rates(start_date: str, end_date: str, base: str = "EUR", symbols: str | None = None) -> dict:
    """
    Retrieves exchange rates over a time period

    Args:
        - start_date: Start date in YYYY-MM-DD format
        - end_date: End date in YYYY-MM-DD format (use '..' for current date)
        - base: Base currency code (default: EUR)
        - symbols: Comma-separated currency codes to filter (optional)

    Returns:
        - dict: Time series data with rates for each day in the period
    """
    logger.info(f"Fetching time series rates start: {start_date}  end: {end_date} base: {base} symbols: {symbols}")
    try:
        series_api = f"{API}/{start_date}..{end_date}?base={base}"
        if symbols:
            series_api += f"&symbols={symbols}"
        
        response = requests.get(series_api)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Successfully fetched time series rates from {start_date} to {end_date}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch time series rates: {e}")
        raise e


if __name__ == "__main__":
    import sys
    
    if "--stdio" in sys.argv:
        # MCP stdio mode for Claude Desktop
        mcp.run(transport="stdio")
    else:
        # HTTP mode (default)
        mcp_app = mcp.http_app(path="/mcp")
        uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
