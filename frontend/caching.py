"""Caching wrappers for backend services.

Thin @st.cache_data decorators that delegate to framework-agnostic
backend services. All Streamlit-specific caching lives here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

from backend.services.data_service import (
    fetch_portfolio_stock_data as _fetch_portfolio_stock_data,
    load_stock_symbols as _load_stock_symbols,
    process_portfolio_price_data as _process_portfolio_price_data,
)
from backend.services.optimization_service import (
    HRPResult,
    OptimizationResults,
    compute_hrp,
    compute_optimizations,
)

if TYPE_CHECKING:
    pass  # Forward references resolved at runtime


@st.cache_data(max_entries=1)
def load_stock_symbols() -> list[str]:
    """Cached wrapper for backend data service."""
    return _load_stock_symbols()


@st.cache_data
def fetch_portfolio_stock_data(
    symbols: tuple[str, ...],
    start_date_str: str,
    end_date_str: str,
    interval: str,
) -> dict[str, pd.DataFrame]:
    """Cached wrapper for backend data service."""
    return _fetch_portfolio_stock_data(list(symbols), start_date_str, end_date_str, interval)


def process_portfolio_price_data(
    all_historical_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Thin wrapper — no cache needed; input is already cached and transform is cheap."""
    return _process_portfolio_price_data(all_historical_data)


@st.cache_data
def cached_compute_optimizations(
    prices_df: pd.DataFrame,
    risk_aversion: float,
) -> OptimizationResults:
    """Cached wrapper for backend optimization service."""
    return compute_optimizations(prices_df, risk_aversion)


@st.cache_data
def cached_compute_hrp(returns: pd.DataFrame) -> HRPResult:
    """Cached wrapper for backend optimization service."""
    return compute_hrp(returns)