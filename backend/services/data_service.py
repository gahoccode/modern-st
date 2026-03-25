"""Data fetching service for Vietnamese stock market data.

Framework-agnostic — no Streamlit imports. Caching is handled by the frontend layer.
"""

import pandas as pd
from vnstock import Listing, Quote

DEFAULT_SYMBOLS: list[str] = ["REE", "HPG", "FMC", "DHG", "FPT", "DHC", "GMD"]


def load_stock_symbols() -> list[str]:
    """Load all valid stock symbols from vnstock Listing API."""
    symbols_df = Listing().all_symbols()
    return sorted(symbols_df["symbol"].tolist())


def fetch_portfolio_stock_data(
    symbols: list[str],
    start_date_str: str,
    end_date_str: str,
    interval: str,
) -> dict[str, pd.DataFrame]:
    """Fetch historical stock data for multiple symbols via vnstock API.

    Raises:
        ValueError: If fetching data for a symbol fails.
    """
    all_data: dict[str, pd.DataFrame] = {}

    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol)
            historical_data = quote.history(
                start=start_date_str, end=end_date_str, interval=interval, to_df=True
            )

            if not historical_data.empty:
                all_data[symbol] = historical_data
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {e}") from e

    return all_data


def process_portfolio_price_data(
    all_historical_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Process historical data from multiple stocks into combined price dataframe.

    Collects each symbol's close-price Series and concatenates once (O(N) vs O(N^2) merge).
    """
    series_list: list[pd.Series] = []

    for symbol, data in all_historical_data.items():
        if data.empty:
            continue
        source = data if "time" in data.columns else data.assign(time=data.index)
        series_list.append(source.set_index("time")["close"].rename(symbol))

    if not series_list:
        return pd.DataFrame()

    prices_df = pd.concat(series_list, axis=1).sort_index().dropna()
    return prices_df


def compute_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Compute simple percentage returns from a price matrix."""
    return prices_df.pct_change().dropna()
