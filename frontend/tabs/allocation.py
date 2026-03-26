"""Dollars Allocation tab renderer.

Displays discrete portfolio allocation converting weights to VND share counts.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.services.optimization_service import compute_discrete_allocation


def render_allocation_tab(
    selected_weights: dict[str, float],
    prices_df: pd.DataFrame,
    portfolio_choice: str,
    symbols: list[str],
) -> None:
    """Render the Dollars Allocation tab."""
    st.subheader("Discrete Portfolio Allocation")

    portfolio_value = st.number_input(
        "Portfolio Value (VND)",
        min_value=1000000,
        max_value=100000000000,
        value=100000000,
        step=1000000,
        help="Enter your total portfolio value in Vietnamese Dong (VND)",
    )

    symbol_display = ", ".join(symbols[:3]) + ("..." if len(symbols) > 3 else "")
    st.info(f"**Using Strategy**: {portfolio_choice} | **Symbols**: {symbol_display}")

    if st.button("Calculate Allocation", key="discrete_allocation"):
        try:
            alloc_result = compute_discrete_allocation(
                selected_weights, prices_df, portfolio_value
            )
            allocation = alloc_result.allocation
            leftover = alloc_result.leftover
            latest_prices_actual = alloc_result.latest_prices_actual

            st.success(f"Allocation calculated successfully for {portfolio_choice}!")

            st.subheader("Stock Allocation")
            allocation_df = pd.DataFrame(list(allocation.items()), columns=["Symbol", "Shares"])
            allocation_df["Latest Price (VND)"] = allocation_df["Symbol"].map(latest_prices_actual)
            allocation_df["Total Value (VND)"] = (
                allocation_df["Shares"] * allocation_df["Latest Price (VND)"]
            )
            allocation_df["Weight %"] = (
                allocation_df["Total Value (VND)"] / portfolio_value * 100
            ).round(2)

            allocation_df["Latest Price (VND)"] = allocation_df["Latest Price (VND)"].apply(
                lambda x: f"{x:,.0f}"
            )
            allocation_df["Total Value (VND)"] = allocation_df["Total Value (VND)"].apply(
                lambda x: f"{x:,.0f}"
            )

            st.dataframe(allocation_df, hide_index=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                allocated_value = portfolio_value - leftover
                st.metric(
                    "Allocated Amount",
                    f"{allocated_value:,.0f} VND",
                    f"{(allocated_value / portfolio_value * 100):.1f}% of portfolio",
                )

            with col2:
                st.metric(
                    "Leftover Cash",
                    f"{leftover:,.0f} VND",
                    f"{(leftover / portfolio_value * 100):.1f}% of portfolio",
                )

            with col3:
                total_stocks = len(allocation)
                st.metric("Stocks to Buy", total_stocks)

            st.subheader("Investment Summary")
            alloc_pct = allocated_value / portfolio_value * 100
            left_pct = leftover / portfolio_value * 100
            st.info(f"""
            **Portfolio Strategy**: {portfolio_choice}
            **Total Investment**: {portfolio_value:,.0f} VND
            **Allocated**: {allocated_value:,.0f} VND ({alloc_pct:.1f}%)
            **Remaining Cash**: {leftover:,.0f} VND ({left_pct:.1f}%)
            **Number of Stocks**: {total_stocks} stocks
            """)

        except Exception as e:
            st.error(f"Error calculating allocation: {str(e)}")
            st.error("Please ensure you have selected stocks and loaded price data first.")
    else:
        st.info(
            "Click 'Calculate Allocation' to see how many shares to buy"
            " for each stock based on your selected portfolio strategy"
            " and investment amount."
        )