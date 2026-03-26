"""Frontend module for Streamlit UI components.

This package contains all Streamlit-specific code, keeping the backend
framework-agnostic. Components here handle presentation, caching wrappers,
and user interaction.
"""

from frontend.caching import (
    cached_compute_hrp,
    cached_compute_optimizations,
    fetch_portfolio_stock_data,
    load_stock_symbols,
)
from frontend.components import (
    display_data_summary,
    display_performance_metrics,
    display_pie_chart,
    display_weights_table,
    inject_custom_success_styling,
)

__all__ = [
    # caching
    "load_stock_symbols",
    "fetch_portfolio_stock_data",
    "cached_compute_optimizations",
    "cached_compute_hrp",
    # components
    "display_weights_table",
    "display_pie_chart",
    "inject_custom_success_styling",
    "display_performance_metrics",
    "display_data_summary",
]