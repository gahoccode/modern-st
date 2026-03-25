"""Portfolio optimization service using PyPortfolioOpt.

Framework-agnostic — no Streamlit imports. Caching is handled by the frontend layer.
"""

from dataclasses import dataclass

import pandas as pd
from pypfopt import (
    DiscreteAllocation,
    EfficientFrontier,
    HRPOpt,
    expected_returns,
    risk_models,
)
from pypfopt.discrete_allocation import get_latest_prices

VNSTOCK_PRICE_UNIT = 1000

STRATEGY_MAP: dict[str, tuple[str, str]] = {
    "Max Sharpe Portfolio": ("Max Sharpe", "Max_Sharpe_Portfolio"),
    "Min Volatility Portfolio": ("Min Volatility", "Min_Volatility_Portfolio"),
    "Max Utility Portfolio": ("Max Utility", "Max_Utility_Portfolio"),
}
STRATEGY_CHOICES: list[str] = list(STRATEGY_MAP.keys())


@dataclass
class PortfolioResult:
    """Result of a single portfolio optimization strategy."""

    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float


@dataclass
class OptimizationResults:
    """Combined results from all three optimization strategies."""

    max_sharpe: PortfolioResult
    min_volatility: PortfolioResult
    max_utility: PortfolioResult
    mu: pd.Series
    cov_matrix: pd.DataFrame

    def weights_by_strategy(self) -> dict[str, dict[str, float]]:
        """Return strategy-slug to weights mapping."""
        return {
            "max_sharpe": self.max_sharpe.weights,
            "min_volatility": self.min_volatility.weights,
            "max_utility": self.max_utility.weights,
        }


@dataclass
class HRPResult:
    """Result of Hierarchical Risk Parity optimization."""

    weights: dict[str, float]
    hrp_instance: HRPOpt


@dataclass
class AllocationResult:
    """Result of discrete portfolio allocation."""

    allocation: dict[str, int]
    leftover: float
    latest_prices_actual: pd.Series


def compute_optimizations(
    prices_df: pd.DataFrame,
    risk_aversion: float,
) -> OptimizationResults:
    """Run all three optimization strategies on the price data.

    Computes Max Sharpe, Min Volatility, and Max Utility portfolios.
    """
    mu = expected_returns.mean_historical_return(prices_df)
    cov_matrix = risk_models.sample_cov(prices_df)

    # Max Sharpe Ratio
    ef_tangent = EfficientFrontier(mu, cov_matrix)
    ef_tangent.max_sharpe()
    weights_max_sharpe = ef_tangent.clean_weights()
    ret_tangent, std_tangent, sharpe = ef_tangent.portfolio_performance()

    # Min Volatility
    ef_min_vol = EfficientFrontier(mu, cov_matrix)
    ef_min_vol.min_volatility()
    weights_min_vol = ef_min_vol.clean_weights()
    ret_min_vol, std_min_vol, sharpe_min_vol = ef_min_vol.portfolio_performance()

    # Max Utility
    ef_max_utility = EfficientFrontier(mu, cov_matrix)
    ef_max_utility.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
    weights_max_utility = ef_max_utility.clean_weights()
    ret_utility, std_utility, sharpe_utility = ef_max_utility.portfolio_performance()

    return OptimizationResults(
        max_sharpe=PortfolioResult(
            weights=weights_max_sharpe,
            expected_return=ret_tangent,
            volatility=std_tangent,
            sharpe_ratio=sharpe,
        ),
        min_volatility=PortfolioResult(
            weights=weights_min_vol,
            expected_return=ret_min_vol,
            volatility=std_min_vol,
            sharpe_ratio=sharpe_min_vol,
        ),
        max_utility=PortfolioResult(
            weights=weights_max_utility,
            expected_return=ret_utility,
            volatility=std_utility,
            sharpe_ratio=sharpe_utility,
        ),
        mu=mu,
        cov_matrix=cov_matrix,
    )


def compute_single_strategy(
    prices_df: pd.DataFrame,
    strategy: str,
    risk_aversion: float = 1.0,
) -> PortfolioResult:
    """Run a single optimization strategy and return its result."""
    mu = expected_returns.mean_historical_return(prices_df)
    cov_matrix = risk_models.sample_cov(prices_df)
    ef = EfficientFrontier(mu, cov_matrix)
    if strategy == "max_sharpe":
        ef.max_sharpe()
    elif strategy == "min_volatility":
        ef.min_volatility()
    else:
        ef.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
    weights = ef.clean_weights()
    ret, vol, sharpe = ef.portfolio_performance()
    return PortfolioResult(
        weights=weights, expected_return=ret, volatility=vol, sharpe_ratio=sharpe
    )


def compute_hrp(returns: pd.DataFrame) -> HRPResult:
    """Run Hierarchical Risk Parity optimization.

    Returns weights and the HRPOpt instance (needed for dendrogram plotting).
    """
    hrp = HRPOpt(returns=returns)
    weights = hrp.optimize()
    return HRPResult(weights=weights, hrp_instance=hrp)


def compute_discrete_allocation(
    weights: dict[str, float],
    prices_df: pd.DataFrame,
    portfolio_value: float,
) -> AllocationResult:
    """Convert portfolio weights to discrete share counts.

    Prices from vnstock are in thousands; multiplied by VNSTOCK_PRICE_UNIT for actual VND.
    """
    latest_prices = get_latest_prices(prices_df)
    latest_prices_actual = latest_prices * VNSTOCK_PRICE_UNIT

    da = DiscreteAllocation(
        weights,
        latest_prices_actual,
        total_portfolio_value=portfolio_value,
    )
    allocation, leftover = da.greedy_portfolio()

    return AllocationResult(
        allocation=allocation,
        leftover=leftover,
        latest_prices_actual=latest_prices_actual,
    )
