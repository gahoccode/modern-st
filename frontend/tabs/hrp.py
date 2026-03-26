"""Hierarchical Risk Parity tab renderer.

Displays HRP portfolio weights and dendrogram visualization.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pypfopt import plotting

from frontend.caching import cached_compute_hrp
from frontend.components import display_weights_table


def render_hrp_tab(returns: pd.DataFrame) -> None:
    """Render the Hierarchical Risk Parity tab."""
    hrp_result = cached_compute_hrp(returns)

    st.subheader("HRP Portfolio Weights")
    display_weights_table(hrp_result.weights, "HRP Portfolio")

    st.subheader("HRP Dendrogram")
    fig_dendro, ax_dendro = plt.subplots(figsize=(12, 8))
    plotting.plot_dendrogram(hrp_result.hrp_instance, ax=ax_dendro, show_tickers=True)
    st.pyplot(fig_dendro)
    plt.close(fig_dendro)