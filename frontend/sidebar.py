"""Sidebar widget definitions and input validation.

Contains the render_sidebar function that returns a dataclass with all
user inputs, plus validation logic for the inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

from backend.services.data_service import DEFAULT_SYMBOLS
from frontend.caching import load_stock_symbols


@dataclass
class SidebarInputs:
    """User inputs from the sidebar."""

    symbols: list[str]
    start_date: date
    end_date: date
    risk_aversion: float
    colormap: str
    interval: str = "1D"

    @property
    def start_date_str(self) -> str:
        """Return start date as YYYY-MM-DD string."""
        return self.start_date.strftime("%Y-%m-%d")

    @property
    def end_date_str(self) -> str:
        """Return end date as YYYY-MM-DD string."""
        return self.end_date.strftime("%Y-%m-%d")

    def validate(self) -> None:
        """Validate inputs and raise ValueError with user-friendly message if invalid."""
        if len(self.symbols) < 2:
            raise ValueError("Please select at least 2 ticker symbols.")

        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date.")


COLORMAP_OPTIONS = [
    "copper",
    "gist_heat",
    "Greys",
    "gist_yarg",
    "gist_gray",
    "cividis",
    "magma",
    "inferno",
    "plasma",
    "viridis",
]


def render_sidebar() -> SidebarInputs:
    """Render sidebar widgets and return collected inputs as a dataclass."""
    st.sidebar.header("Portfolio Configuration")

    try:
        stock_symbols_list = load_stock_symbols()
    except Exception:
        stock_symbols_list = DEFAULT_SYMBOLS

    symbols = st.sidebar.multiselect(
        "Select ticker symbols:",
        options=stock_symbols_list,
        default=["REE", "HPG", "FMC"],
        placeholder="Choose stock symbols...",
        help="Select multiple stock symbols for portfolio optimization",
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=pd.to_datetime("2024-01-01"),
            max_value=pd.to_datetime("today"),
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=pd.to_datetime("today") - pd.Timedelta(days=1),
            max_value=pd.to_datetime("today"),
        )

    risk_aversion = st.sidebar.number_input(
        "Risk Aversion Parameter", value=1.0, min_value=0.1, max_value=10.0, step=0.1
    )

    colormap = st.sidebar.selectbox(
        "Scatter Plot Colormap",
        options=COLORMAP_OPTIONS,
        index=0,
        help="Choose the color scheme for the efficient frontier scatter plot",
    )

    return SidebarInputs(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        risk_aversion=risk_aversion,
        colormap=colormap,
    )