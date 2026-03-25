"""Shared utilities for the pyopt API layer."""

from __future__ import annotations

import pandas as pd

from backend.api.exceptions import DataFetchError, ProcessingError
from backend.services.data_service import fetch_portfolio_stock_data, process_portfolio_price_data


def get_price_matrix(
    symbols: list[str], start_date: str, end_date: str
) -> pd.DataFrame:
    """Fetch raw stock data and process into a price matrix.

    Raises:
        DataFetchError: If no data is returned for the given symbols.
        ProcessingError: If the processed price matrix is empty.
    """
    raw = fetch_portfolio_stock_data(symbols, start_date, end_date, "1D")
    if not raw:
        raise DataFetchError(f"No data fetched for symbols: {symbols}")
    prices_df = process_portfolio_price_data(raw)
    if prices_df.empty:
        raise ProcessingError("No valid price data after processing.")
    return prices_df
