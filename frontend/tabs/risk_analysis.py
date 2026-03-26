"""Risk Analysis tab renderer.

Displays risk metrics table, drawdown analysis, and return distribution plots.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import riskfolio as rp
import streamlit as st


def render_risk_analysis_tab(
    returns: pd.DataFrame,
    selected_weights: dict[str, float],
    portfolio_choice: str,
    portfolio_label: str,
    symbols: list[str],
) -> None:
    """Render the Risk Analysis tab."""
    st.subheader("Risk Analysis Table")

    symbol_display = ", ".join(symbols[:3]) + ("..." if len(symbols) > 3 else "")
    st.info(f"**Analyzing Strategy**: {portfolio_choice} | **Symbols**: {symbol_display}")

    selected_weights_df = pd.DataFrame.from_dict(
        selected_weights, orient="index", columns=["Weights"]
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    ax = rp.plot_table(
        returns=returns,
        w=selected_weights_df,
        MAR=0,
        alpha=0.05,
        ax=ax,
    )

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Portfolio Drawdown Analysis")

    fig_drawdown, ax_drawdown = plt.subplots(figsize=(12, 8))

    ax_drawdown = rp.plot_drawdown(
        returns=returns,
        w=selected_weights_df,
        alpha=0.05,
        kappa=0.3,
        solver="CLARABEL",
        height=8,
        width=10,
        height_ratios=[2, 3],
        ax=ax_drawdown,
    )

    st.pyplot(fig_drawdown)
    plt.close(fig_drawdown)

    st.subheader("Portfolio Returns Risk Measures")

    fig_range, ax_range = plt.subplots(figsize=(12, 6))

    ax_range = rp.plot_range(
        returns=returns,
        w=selected_weights_df,
        alpha=0.05,
        a_sim=100,
        beta=None,
        b_sim=None,
        bins=50,
        height=6,
        width=10,
        ax=ax_range,
    )

    st.pyplot(fig_range)
    plt.close(fig_range)

    with st.expander("Understanding the Risk Analysis Table"):
        st.markdown(f"""
        This table provides comprehensive risk metrics for your {portfolio_label} portfolio:

        **Key Metrics:**
        - **Expected Return**: Annualized expected portfolio return
        - **Volatility**: Portfolio standard deviation (risk measure)
        - **Sharpe Ratio**: Risk-adjusted return measure
        - **VaR**: Value at Risk - potential loss at 95% confidence
        - **CVaR**: Conditional Value at Risk - expected loss beyond VaR
        - **Max Drawdown**: Largest peak-to-trough decline
        - **Calmar Ratio**: Return to max drawdown ratio

        *Generated using riskfolio-lib risk analysis framework*
        """)