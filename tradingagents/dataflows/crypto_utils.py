import requests
import pandas as pd
from datetime import datetime

# Mapping of common tickers to CoinGecko IDs
COIN_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "LTC": "litecoin",
    "DOGE": "dogecoin",
    "ADA": "cardano",
}


def _to_id(symbol: str) -> str:
    symbol = symbol.upper().replace("-USD", "")
    return COIN_MAP.get(symbol, symbol.lower())


def get_crypto_price_history(
    symbol: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Fetch historical price data from CoinGecko."""
    coin_id = _to_id(symbol)
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {"vs_currency": "usd", "from": start_ts, "to": end_ts}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("prices", [])
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_crypto_metrics(symbol: str) -> pd.DataFrame:
    """Fetch basic market metrics from CoinGecko."""
    coin_id = _to_id(symbol)
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    mkt = resp.json().get("market_data", {})
    metrics = {
        "current_price_usd": mkt.get("current_price", {}).get("usd"),
        "market_cap_usd": mkt.get("market_cap", {}).get("usd"),
        "total_volume_usd": mkt.get("total_volume", {}).get("usd"),
        "high_24h": mkt.get("high_24h", {}).get("usd"),
        "low_24h": mkt.get("low_24h", {}).get("usd"),
    }
    return pd.DataFrame([metrics])
