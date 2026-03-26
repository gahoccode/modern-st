"""Tests for backend/services/optimization_service.py."""

import math

import pandas as pd
import pytest

from backend.services.optimization_service import (
    VNSTOCK_PRICE_UNIT,
    compute_discrete_allocation,
    compute_hrp,
    compute_optimizations,
    compute_single_strategy,
)


class TestComputeOptimizations:
    """Tests for compute_optimizations function."""

    def test_returns_all_strategies(self, sample_prices_df: pd.DataFrame) -> None:
        """compute_optimizations returns all three strategy results."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        assert results.max_sharpe is not None
        assert results.min_volatility is not None
        assert results.max_utility is not None

    def test_weights_sum_to_one(self, sample_prices_df: pd.DataFrame) -> None:
        """Portfolio weights must sum to approximately 1.0."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        for strategy_name, result in [
            ("max_sharpe", results.max_sharpe),
            ("min_volatility", results.min_volatility),
            ("max_utility", results.max_utility),
        ]:
            total_weight = sum(result.weights.values())
            assert math.isclose(total_weight, 1.0, abs_tol=1e-6), (
                f"{strategy_name} weights sum to {total_weight}, expected 1.0"
            )

    def test_expected_return_reasonable(self, sample_prices_df: pd.DataFrame) -> None:
        """Expected returns should be within plausible range (-50% to 200% annual)."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        for strategy_name, result in [
            ("max_sharpe", results.max_sharpe),
            ("min_volatility", results.min_volatility),
            ("max_utility", results.max_utility),
        ]:
            assert -0.5 <= result.expected_return <= 2.0, (
                f"{strategy_name} expected_return {result.expected_return} out of range"
            )

    def test_volatility_positive(self, sample_prices_df: pd.DataFrame) -> None:
        """Volatility must be positive."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        for strategy_name, result in [
            ("max_sharpe", results.max_sharpe),
            ("min_volatility", results.min_volatility),
            ("max_utility", results.max_utility),
        ]:
            assert result.volatility > 0, f"{strategy_name} volatility must be positive"

    def test_sharpe_ratio_reasonable(self, sample_prices_df: pd.DataFrame) -> None:
        """Sharpe ratio should be within plausible range."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        for strategy_name, result in [
            ("max_sharpe", results.max_sharpe),
            ("min_volatility", results.min_volatility),
            ("max_utility", results.max_utility),
        ]:
            assert -3.0 <= result.sharpe_ratio <= 5.0, (
                f"{strategy_name} sharpe_ratio {result.sharpe_ratio} out of range"
            )

    def test_mu_and_cov_matrix_returned(self, sample_prices_df: pd.DataFrame) -> None:
        """Results include expected returns vector and covariance matrix."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)

        assert results.mu is not None
        assert results.cov_matrix is not None
        assert len(results.mu) == len(sample_prices_df.columns)
        assert results.cov_matrix.shape == (len(sample_prices_df.columns), len(sample_prices_df.columns))

    def test_weights_by_strategy_mapping(self, sample_prices_df: pd.DataFrame) -> None:
        """weights_by_strategy returns correct mapping."""
        results = compute_optimizations(sample_prices_df, risk_aversion=1.0)
        mapping = results.weights_by_strategy()

        assert "max_sharpe" in mapping
        assert "min_volatility" in mapping
        assert "max_utility" in mapping
        assert mapping["max_sharpe"] == results.max_sharpe.weights


class TestComputeSingleStrategy:
    """Tests for compute_single_strategy function."""

    def test_max_sharpe_strategy(self, sample_prices_df: pd.DataFrame) -> None:
        """Max Sharpe strategy returns valid result."""
        result = compute_single_strategy(sample_prices_df, "max_sharpe")

        assert result.weights is not None
        assert result.sharpe_ratio is not None
        assert math.isclose(sum(result.weights.values()), 1.0, abs_tol=1e-6)

    def test_min_volatility_strategy(self, sample_prices_df: pd.DataFrame) -> None:
        """Min Volatility strategy returns valid result."""
        result = compute_single_strategy(sample_prices_df, "min_volatility")

        assert result.weights is not None
        assert result.volatility > 0
        assert math.isclose(sum(result.weights.values()), 1.0, abs_tol=1e-6)

    def test_max_utility_strategy(self, sample_prices_df: pd.DataFrame) -> None:
        """Max Utility strategy returns valid result with custom risk aversion."""
        result = compute_single_strategy(sample_prices_df, "max_utility", risk_aversion=2.0)

        assert result.weights is not None
        assert math.isclose(sum(result.weights.values()), 1.0, abs_tol=1e-6)

    def test_strategy_characteristics(self, sample_prices_df: pd.DataFrame) -> None:
        """Min Volatility should have lower or equal volatility than Max Sharpe."""
        min_vol = compute_single_strategy(sample_prices_df, "min_volatility")
        max_sharpe = compute_single_strategy(sample_prices_df, "max_sharpe")

        # Min Volatility should generally have lower volatility
        assert min_vol.volatility <= max_sharpe.volatility + 0.01, (
            f"Min Vol volatility ({min_vol.volatility}) should be <= Max Sharpe ({max_sharpe.volatility})"
        )


class TestComputeHRP:
    """Tests for compute_hrp function."""

    def test_weights_sum_to_one(self, sample_returns_df: pd.DataFrame) -> None:
        """HRP weights must sum to approximately 1.0."""
        result = compute_hrp(sample_returns_df)

        total_weight = sum(result.weights.values())
        assert math.isclose(total_weight, 1.0, abs_tol=1e-6), (
            f"HRP weights sum to {total_weight}, expected 1.0"
        )

    def test_returns_weights_dict(self, sample_returns_df: pd.DataFrame) -> None:
        """HRP returns weights dict with correct symbols."""
        result = compute_hrp(sample_returns_df)

        assert isinstance(result.weights, dict)
        assert set(result.weights.keys()) == set(sample_returns_df.columns)

    def test_hrp_instance_returned(self, sample_returns_df: pd.DataFrame) -> None:
        """HRP returns HRPOpt instance for dendrogram plotting."""
        result = compute_hrp(sample_returns_df)

        assert result.hrp_instance is not None

    def test_all_weights_positive(self, sample_returns_df: pd.DataFrame) -> None:
        """All HRP weights should be non-negative."""
        result = compute_hrp(sample_returns_df)

        for symbol, weight in result.weights.items():
            assert weight >= 0, f"Weight for {symbol} is negative: {weight}"


class TestComputeDiscreteAllocation:
    """Tests for compute_discrete_allocation function."""

    def test_basic_allocation(self, sample_prices_df: pd.DataFrame, sample_weights: dict[str, float]) -> None:
        """Discrete allocation returns valid allocation and leftover."""
        portfolio_value = 10_000_000  # 10 million VND
        result = compute_discrete_allocation(sample_weights, sample_prices_df, portfolio_value)

        assert isinstance(result.allocation, dict)
        assert result.leftover >= 0

    def test_leftover_less_than_cheapest_share(
        self, sample_prices_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Leftover should be less than the price of the cheapest share."""
        portfolio_value = 10_000_000  # 10 million VND
        result = compute_discrete_allocation(sample_weights, sample_prices_df, portfolio_value)

        # Get the actual prices (in VND, not thousands)
        min_share_price = min(result.latest_prices_actual.values)

        assert result.leftover < min_share_price, (
            f"Leftover ({result.leftover}) should be < cheapest share ({min_share_price})"
        )

    def test_vnstock_price_unit_applied(
        self, sample_prices_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Prices should be multiplied by VNSTOCK_PRICE_UNIT (1000)."""
        portfolio_value = 10_000_000  # 10 million VND
        result = compute_discrete_allocation(sample_weights, sample_prices_df, portfolio_value)

        # The latest_prices_actual should be 1000x the raw prices
        raw_latest = sample_prices_df.iloc[-1]
        for symbol in sample_weights.keys():
            expected_price = raw_latest[symbol] * VNSTOCK_PRICE_UNIT
            actual_price = result.latest_prices_actual[symbol]
            assert math.isclose(actual_price, expected_price, rel_tol=1e-6), (
                f"Price for {symbol}: expected {expected_price}, got {actual_price}"
            )

    def test_allocation_integer_shares(
        self, sample_prices_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Allocated shares should be whole numbers."""
        portfolio_value = 10_000_000  # 10 million VND
        result = compute_discrete_allocation(sample_weights, sample_prices_df, portfolio_value)

        for symbol, shares in result.allocation.items():
            assert isinstance(shares, int) or shares == int(shares), (
                f"Shares for {symbol} should be integer, got {shares}"
            )

    def test_total_allocated_value(
        self, sample_prices_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Allocated value plus leftover should not exceed portfolio value."""
        portfolio_value = 10_000_000  # 10 million VND
        result = compute_discrete_allocation(sample_weights, sample_prices_df, portfolio_value)

        allocated_value = sum(
            result.allocation.get(symbol, 0) * result.latest_prices_actual[symbol]
            for symbol in sample_prices_df.columns
        )

        assert allocated_value + result.leftover <= portfolio_value + 1, (
            f"Allocated ({allocated_value}) + leftover ({result.leftover}) > portfolio ({portfolio_value})"
        )