"""Reusable UI components for Streamlit application.

Contains display helpers for weights tables, pie charts, metrics,
and other visual elements used across multiple tabs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import altair as alt
import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from backend.services.optimization_service import PortfolioResult


def display_weights_table(weights: dict[str, float], label: str) -> None:
    """Render a weights dict as a formatted Streamlit dataframe."""
    st.write(f"**{label}**")
    df = pd.DataFrame(list(weights.items()), columns=["Symbol", "Weight"])
    df["Weight"] = df["Weight"].apply(lambda x: f"{x:.2%}")
    st.dataframe(df, hide_index=True)


def display_pie_chart(
    weights: dict[str, float],
    title: str,
    colors: list[str] | None = None,
) -> None:
    """Create and display an Altair donut chart for portfolio weights."""
    if colors is None:
        colors = ["#56524D", "#76706C", "#AAA39F"]

    data = pd.DataFrame(list(weights.items()), columns=["Symbol", "Weight"])
    data = data[data["Weight"] > 0.01].sort_values("Weight", ascending=False)

    if len(data) == 0:
        st.write(f"No significant weights in {title}")
        return

    fill = (
        colors[: len(data)]
        if len(data) <= len(colors)
        else colors + ["#D3D3D3"] * (len(data) - len(colors))
    )
    data["color"] = fill

    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=50, stroke="white", strokeWidth=2)
        .encode(
            theta=alt.Theta("Weight:Q", title="Weight"),
            color=alt.Color(
                "Symbol:N",
                scale=alt.Scale(range=data["color"].tolist()),
                legend=alt.Legend(title="Symbols"),
            ),
            tooltip=[
                alt.Tooltip("Symbol:N", title="Symbol"),
                alt.Tooltip("Weight:Q", title="Weight", format=".2%"),
            ],
        )
        .properties(width=350, height=350, title=title)
    )

    st.altair_chart(chart, width="stretch")


def inject_custom_success_styling() -> None:
    """Inject custom CSS styling for Streamlit success alerts with earth-tone theme."""
    st.html("""
<style>
div[data-testid="stAlert"][data-baseweb="notification"] {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}
.stAlert {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}
.stSuccess, .st-success {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}
div[data-testid="stAlert"] > div {
    background-color: #D4D4D4 !important;
    color: #56524D !important;
}
div[data-testid="stAlert"] .stMarkdown {
    color: #56524D !important;
}
div[data-testid="stAlert"] p {
    color: #56524D !important;
}
.stMarkdownContainer {
    background-color: #76706C !important;
}
</style>
""")


def display_performance_metrics(
    max_sharpe: PortfolioResult,
    min_volatility: PortfolioResult,
    max_utility: PortfolioResult,
) -> None:
    """Display 3-column metrics for all optimization strategies."""
    st.subheader("Performance Metrics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Max Sharpe Portfolio",
            f"{max_sharpe.sharpe_ratio:.4f}",
            f"Return: {(max_sharpe.expected_return * 100):.1f}%",
        )

    with col2:
        st.metric(
            "Min Volatility Portfolio",
            f"{min_volatility.sharpe_ratio:.4f}",
            f"Return: {(min_volatility.expected_return * 100):.1f}%",
        )

    with col3:
        st.metric(
            "Max Utility Portfolio",
            f"{max_utility.sharpe_ratio:.4f}",
            f"Return: {(max_utility.expected_return * 100):.1f}%",
        )


def display_data_summary(prices_df: pd.DataFrame, symbols: list[str]) -> None:
    """Display symbols count, data points, and price data preview."""
    st.header("Data Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Symbols", len(symbols))
    with col2:
        st.metric("Data Points", len(prices_df))

    with st.expander("View Price Data"):
        view_option = st.radio(
            "Display option:",
            ["First 5 rows", "Last 5 rows"],
            horizontal=True,
            key="price_data_view",
        )

        if view_option == "First 5 rows":
            st.dataframe(prices_df.head())
        else:
            st.dataframe(prices_df.tail())

        st.write(f"Shape: {prices_df.shape}")