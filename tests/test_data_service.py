"""Tests for backend/services/data_service.py."""

import pandas as pd
import pytest

from backend.services.data_service import (
    compute_returns,
    process_portfolio_price_data,
)


class TestProcessPortfolioPriceData:
    """Tests for process_portfolio_price_data function."""

    def test_combines_symbols(self, mock_vnstock_data_multi: dict[str, pd.DataFrame]) -> None:
        """Function combines multiple symbols into single DataFrame."""
        result = process_portfolio_price_data(mock_vnstock_data_multi)

        assert isinstance(result, pd.DataFrame)
        assert set(result.columns) == {"FPT", "HPG", "VNM"}
        assert len(result) == 100  # 100 rows from fixture

    def test_handles_empty_input(self) -> None:
        """Empty input returns empty DataFrame."""
        result = process_portfolio_price_data({})

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_drops_na(self, mock_vnstock_data_multi: dict[str, pd.DataFrame]) -> None:
        """Result has no NaN values after processing."""
        result = process_portfolio_price_data(mock_vnstock_data_multi)

        assert not result.isna().any().any(), "Result contains NaN values"

    def test_sorts_by_time(self, mock_vnstock_data_multi: dict[str, pd.DataFrame]) -> None:
        """Result index is sorted chronologically."""
        result = process_portfolio_price_data(mock_vnstock_data_multi)

        assert result.index.is_monotonic_increasing, "Index not sorted by time"

    def test_uses_close_prices(self, mock_vnstock_data_multi: dict[str, pd.DataFrame]) -> None:
        """Function extracts close prices from OHLCV data."""
        result = process_portfolio_price_data(mock_vnstock_data_multi)

        # Verify values match close column from input
        fpt_close = mock_vnstock_data_multi["FPT"]["close"].values
        assert all(result["FPT"].values == fpt_close)

    def test_handles_time_as_index(self) -> None:
        """Function handles case where time is index, not column."""
        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        data = pd.DataFrame(
            {"close": range(50, 100)},
            index=dates,
        )

        input_data = {"FPT": data}
        result = process_portfolio_price_data(input_data)

        assert not result.empty
        assert "FPT" in result.columns


class TestComputeReturns:
    """Tests for compute_returns function."""

    def test_calculates_pct_change(self, sample_prices_df: pd.DataFrame) -> None:
        """Function computes percentage change correctly."""
        result = compute_returns(sample_prices_df)

        # Manually compute expected
        expected = sample_prices_df.pct_change().dropna()

        pd.testing.assert_frame_equal(result, expected)

    def test_drops_first_row(self, sample_prices_df: pd.DataFrame) -> None:
        """First row is dropped due to NaN from pct_change."""
        result = compute_returns(sample_prices_df)

        assert len(result) == len(sample_prices_df) - 1

    def test_returns_dataframe(self, sample_prices_df: pd.DataFrame) -> None:
        """Returns a DataFrame."""
        result = compute_returns(sample_prices_df)

        assert isinstance(result, pd.DataFrame)

    def test_preserves_columns(self, sample_prices_df: pd.DataFrame) -> None:
        """Column names are preserved."""
        result = compute_returns(sample_prices_df)

        assert list(result.columns) == list(sample_prices_df.columns)

    def test_no_nan_values(self, sample_prices_df: pd.DataFrame) -> None:
        """Result contains no NaN values."""
        result = compute_returns(sample_prices_df)

        assert not result.isna().any().any()

    def test_values_in_reasonable_range(self, sample_prices_df: pd.DataFrame) -> None:
        """Return values should be in reasonable range (e.g., -50% to +50%)."""
        result = compute_returns(sample_prices_df)

        assert (result >= -0.5).all().all(), "Returns below -50%"
        assert (result <= 0.5).all().all(), "Returns above 50%"