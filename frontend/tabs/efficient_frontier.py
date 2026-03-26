"""Efficient Frontier & Weights tab renderer.

Displays the efficient frontier plot, random portfolios scatter,
weights tables, and pie charts for all three strategies.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from pypfopt import EfficientFrontier, plotting

from backend.services.optimization_service import OptimizationResults
from frontend.components import display_pie_chart, display_weights_table


def render_efficient_frontier_tab(
    opt_results: OptimizationResults,
    colormap: str,
) -> None:
    """Render the Efficient Frontier & Weights tab."""
    ms = opt_results.max_sharpe
    mv = opt_results.min_volatility
    mu_result = opt_results.max_utility

    st.subheader("Efficient Frontier Analysis")
    fig, ax = plt.subplots(figsize=(12, 8))

    ef_plot = EfficientFrontier(opt_results.mu, opt_results.cov_matrix)
    plotting.plot_efficient_frontier(ef_plot, ax=ax, show_assets=True)

    ax.scatter(
        ms.volatility, ms.expected_return,
        marker="*", s=200, c="red", label="Max Sharpe", zorder=5,
    )
    ax.scatter(
        mv.volatility, mv.expected_return,
        marker="*", s=200, c="green", label="Min Volatility", zorder=5,
    )
    ax.scatter(
        mu_result.volatility, mu_result.expected_return,
        marker="*", s=200, c="blue", label="Max Utility", zorder=5,
    )

    n_samples = 5000
    w = np.random.dirichlet(np.ones(ef_plot.n_assets), n_samples)
    rets = w.dot(ef_plot.expected_returns)
    stds = np.sqrt(np.einsum("ij,jk,ik->i", w, ef_plot.cov_matrix, w))
    sharpes = rets / stds

    scatter = ax.scatter(stds, rets, marker=".", c=sharpes, cmap=colormap, alpha=0.6)
    plt.colorbar(scatter, label="Sharpe Ratio")

    ax.set_title("Efficient Frontier with Random Portfolios")
    ax.set_xlabel("Annual Volatility")
    ax.set_ylabel("Annual Return")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Portfolio Weights")
    col1, col2, col3 = st.columns(3)

    with col1:
        display_weights_table(ms.weights, "Max Sharpe Portfolio")

    with col2:
        display_weights_table(mv.weights, "Min Volatility Portfolio")

    with col3:
        display_weights_table(mu_result.weights, "Max Utility Portfolio")

    st.subheader("Portfolio Weights Visualization")

    col1, col2, col3 = st.columns(3)

    with col1:
        display_pie_chart(ms.weights, "Max Sharpe Portfolio")

    with col2:
        display_pie_chart(mv.weights, "Min Volatility Portfolio")

    with col3:
        display_pie_chart(mu_result.weights, "Max Utility Portfolio")

    st.subheader("Detailed Performance Analysis")
    performance_df = pd.DataFrame(
        {
            "Portfolio": ["Max Sharpe", "Min Volatility", "Max Utility"],
            "Expected Return": [
                f"{ms.expected_return:.4f}",
                f"{mv.expected_return:.4f}",
                f"{mu_result.expected_return:.4f}",
            ],
            "Volatility": [
                f"{ms.volatility:.4f}",
                f"{mv.volatility:.4f}",
                f"{mu_result.volatility:.4f}",
            ],
            "Sharpe Ratio": [
                f"{ms.sharpe_ratio:.4f}",
                f"{mv.sharpe_ratio:.4f}",
                f"{mu_result.sharpe_ratio:.4f}",
            ],
        }
    )
    st.dataframe(performance_df, hide_index=True)