"""Main Streamlit application entry point.

Orchestration layer that imports from frontend modules and backend services.
All Streamlit-specific code lives in the frontend package.
"""

from __future__ import annotations

import streamlit as st

from backend.services.data_service import compute_returns
from backend.services.optimization_service import STRATEGY_CHOICES, STRATEGY_MAP
from frontend.caching import (
    cached_compute_optimizations,
    fetch_portfolio_stock_data,
    process_portfolio_price_data,
)
from frontend.components import (
    display_data_summary,
    display_performance_metrics,
    inject_custom_success_styling,
)
from frontend.sidebar import render_sidebar
from frontend.tabs import (
    render_allocation_tab,
    render_efficient_frontier_tab,
    render_hrp_tab,
    render_report_tab,
    render_risk_analysis_tab,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Stock Portfolio Optimization", page_icon="", layout="wide")

inject_custom_success_styling()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

inputs = render_sidebar()

# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

try:
    inputs.validate()
except ValueError as e:
    st.error(str(e))
    st.stop()

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

try:
    all_historical_data = fetch_portfolio_stock_data(
        tuple(sorted(inputs.symbols)),
        inputs.start_date_str,
        inputs.end_date_str,
        inputs.interval,
    )
except ValueError as e:
    st.error(str(e))
    st.stop()

if not all_historical_data:
    st.error("No data was fetched for any symbol. Please check your inputs.")
    st.stop()

prices_df = process_portfolio_price_data(all_historical_data)

if prices_df.empty:
    st.error("No valid price data after processing.")
    st.stop()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("Stock Portfolio Optimization")
st.write("Optimize your portfolio using Modern Portfolio Theory")

display_data_summary(prices_df, inputs.symbols)

# ---------------------------------------------------------------------------
# Portfolio optimization
# ---------------------------------------------------------------------------

returns = compute_returns(prices_df)
opt_results = cached_compute_optimizations(prices_df, inputs.risk_aversion)

st.header("Portfolio Optimization Results")

display_performance_metrics(
    opt_results.max_sharpe,
    opt_results.min_volatility,
    opt_results.max_utility,
)

# ---------------------------------------------------------------------------
# Strategy selection (shared across tabs)
# ---------------------------------------------------------------------------

portfolio_choice = st.radio(
    "Select Portfolio Strategy:",
    STRATEGY_CHOICES,
    help="This selection applies to Dollar Allocation, Report, and Risk Analysis tabs",
    horizontal=True,
    key="portfolio_strategy_master",
)

portfolio_label, portfolio_name = STRATEGY_MAP[portfolio_choice]
symbol_display = ", ".join(inputs.symbols[:3]) + ("..." if len(inputs.symbols) > 3 else "")

# ---------------------------------------------------------------------------
# Compute weights by strategy (needed for all tabs that use portfolio_choice)
# ---------------------------------------------------------------------------

weights_by_strategy = {
    "Max Sharpe Portfolio": opt_results.max_sharpe.weights,
    "Min Volatility Portfolio": opt_results.min_volatility.weights,
    "Max Utility Portfolio": opt_results.max_utility.weights,
}
selected_weights = weights_by_strategy[portfolio_choice]

# ---------------------------------------------------------------------------
# Lazy tab rendering with segmented control
# ---------------------------------------------------------------------------

TAB_OPTIONS = [
    "Efficient Frontier & Weights",
    "Hierarchical Risk Parity",
    "Dollars Allocation",
    "Report",
    "Risk Analysis",
]

selected_tab = st.segmented_control(
    "View",
    TAB_OPTIONS,
    label_visibility="collapsed",
    selection_mode="single",
    default=TAB_OPTIONS[0],
)

if selected_tab == "Efficient Frontier & Weights":
    render_efficient_frontier_tab(opt_results, inputs.colormap)

elif selected_tab == "Hierarchical Risk Parity":
    render_hrp_tab(returns)

elif selected_tab == "Dollars Allocation":
    render_allocation_tab(selected_weights, prices_df, portfolio_choice, inputs.symbols)

elif selected_tab == "Report":
    render_report_tab(
        returns,
        selected_weights,
        portfolio_choice,
        portfolio_label,
        portfolio_name,
    )

elif selected_tab == "Risk Analysis":
    render_risk_analysis_tab(
        returns,
        selected_weights,
        portfolio_choice,
        portfolio_label,
        inputs.symbols,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    "*Portfolio optimization based on Modern Portfolio Theory."
    " Past performance does not guarantee future results.*"
)
