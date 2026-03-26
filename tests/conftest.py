"""Shared test fixtures for pyopt tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_prices_df() -> pd.DataFrame:
    """Generate deterministic price data for Vietnamese stocks."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    returns = np.random.normal(0.001, 0.02, (100, 3))
    prices = np.cumprod(1 + returns, axis=0) * 100
    return pd.DataFrame(prices, index=dates, columns=["FPT", "HPG", "VNM"])


@pytest.fixture
def sample_returns_df(sample_prices_df: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame computed from prices."""
    return sample_prices_df.pct_change().dropna()


@pytest.fixture
def sample_weights() -> dict[str, float]:
    """Valid portfolio weights for Vietnamese stocks."""
    return {"FPT": 0.4, "HPG": 0.35, "VNM": 0.25}


@pytest.fixture
def mock_vnstock_response() -> pd.DataFrame:
    """Mock vnstock Quote.history() response structure.

    Quote.history() returns OHLCV DataFrame with columns:
    time, open, high, low, close, volume
    The 'time' may be the index or a regular column depending on vnstock version.
    """
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    base_price = 100.0
    returns = np.random.normal(0.001, 0.02, 100)
    closes = np.cumprod(1 + returns) * base_price

    return pd.DataFrame({
        "time": dates,
        "open": closes * np.random.uniform(0.98, 1.02, 100),
        "high": closes * np.random.uniform(1.0, 1.05, 100),
        "low": closes * np.random.uniform(0.95, 1.0, 100),
        "close": closes,
        "volume": np.random.randint(100000, 1000000, 100),
    })


@pytest.fixture
def mock_vnstock_data_multi(mock_vnstock_response: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Mock data for multiple symbols as returned by fetch_portfolio_stock_data."""
    symbols = ["FPT", "HPG", "VNM"]
    return {symbol: mock_vnstock_response.copy() for symbol in symbols}