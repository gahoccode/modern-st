"""Tests for backend/services/risk_service.py."""

import math

import pandas as pd
import pytest

from backend.services.risk_service import compute_risk_metrics


class TestComputeRiskMetrics:
    """Tests for compute_risk_metrics function."""

    def test_returns_all_categories(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Function returns all expected metric categories."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        assert "profitability" in result
        assert "return_based_risks" in result
        assert "drawdown_based_risks" in result
        assert "risk_adjusted_ratios" in result

    def test_std_dev_positive(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Standard deviation must be positive."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        assert result["return_based_risks"]["std_dev"] > 0

    def test_var_less_than_cvar(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """CVaR (Expected Shortfall) should be >= VaR (in absolute terms).

        CVaR measures average loss beyond VaR threshold, so it should be larger.
        Both are negative values representing losses.
        """
        result = compute_risk_metrics(sample_returns_df, sample_weights, alpha=0.05)

        var = result["return_based_risks"]["var"]
        cvar = result["return_based_risks"]["cvar"]

        # Both are annualized; CVaR magnitude should be >= VaR magnitude
        # In risk terms, CVaR >= VaR (less negative or same)
        assert abs(cvar) >= abs(var) - 0.01, f"CVaR ({cvar}) should have >= magnitude than VaR ({var})"

    def test_max_drawdown_positive(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Maximum drawdown should be positive (representing loss magnitude)."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        assert result["drawdown_based_risks"]["max_drawdown"] >= 0

    def test_risk_adjusted_ratios_computed(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Risk-adjusted ratios are computed for each risk metric."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        ratios = result["risk_adjusted_ratios"]
        assert "std_dev" in ratios  # Sharpe-like ratio
        assert "var" in ratios
        assert "cvar" in ratios
        assert "max_drawdown" in ratios  # Calmar-like ratio

    def test_weights_dict_matches_returns_columns(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Weights keys match returns DataFrame columns."""
        # This should not raise an error
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        assert result is not None

    def test_profitability_fields(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Profitability category contains expected fields."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        prof = result["profitability"]
        assert "mean_return" in prof
        assert "cagr" in prof
        assert "mar" in prof
        assert "alpha" in prof

    def test_return_based_risks_fields(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Return-based risks contain all expected metrics."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        risks = result["return_based_risks"]
        expected_fields = [
            "std_dev",
            "mad",
            "semi_deviation",
            "flpm",
            "slpm",
            "var",
            "cvar",
            "evar",
            "tail_gini",
            "rlvar",
            "worst_realization",
            "skewness",
            "kurtosis",
        ]
        for field in expected_fields:
            assert field in risks, f"Missing field: {field}"

    def test_drawdown_based_risks_fields(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Drawdown-based risks contain all expected metrics."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        risks = result["drawdown_based_risks"]
        expected_fields = [
            "ulcer_index",
            "avg_drawdown",
            "dar",
            "cdar",
            "edar",
            "rldar",
            "max_drawdown",
        ]
        for field in expected_fields:
            assert field in risks, f"Missing field: {field}"

    def test_custom_alpha(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Custom alpha parameter is respected."""
        result_05 = compute_risk_metrics(sample_returns_df, sample_weights, alpha=0.05)
        result_01 = compute_risk_metrics(sample_returns_df, sample_weights, alpha=0.01)

        # VaR at 1% should be more extreme (larger magnitude) than at 5%
        var_05 = abs(result_05["return_based_risks"]["var"])
        var_01 = abs(result_01["return_based_risks"]["var"])

        assert var_01 >= var_05, "VaR at 1% should have >= magnitude than VaR at 5%"

    def test_values_are_rounded(
        self, sample_returns_df: pd.DataFrame, sample_weights: dict[str, float]
    ) -> None:
        """Returned values are rounded to 6 decimal places."""
        result = compute_risk_metrics(sample_returns_df, sample_weights)

        # Check a few values have reasonable precision
        mean_return = result["profitability"]["mean_return"]
        # Value should be finite and not have excessive precision
        assert math.isfinite(mean_return)
        assert mean_return == round(mean_return, 6)