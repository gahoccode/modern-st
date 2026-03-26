"""Integration tests for backend/api/routes.py."""

from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.api.routes import api


@pytest.fixture
def client() -> TestClient:
    """Create test client for the API."""
    return TestClient(api)


@pytest.fixture
def mock_empty_fetch() -> dict[str, pd.DataFrame]:
    """Mock empty vnstock response for fetch_portfolio_stock_data."""
    return {"FPT": pd.DataFrame(), "HPG": pd.DataFrame(), "VNM": pd.DataFrame()}


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health(self, client: TestClient) -> None:
        """Health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "pyopt"
        assert "version" in data


class TestInfoEndpoint:
    """Tests for /api/info endpoint."""

    def test_info(self, client: TestClient) -> None:
        """Info endpoint returns app metadata and strategies."""
        response = client.get("/info")

        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "pyopt"
        assert "version" in data
        assert "strategies" in data
        assert len(data["strategies"]) == 3


class TestSymbolsEndpoint:
    """Tests for /api/symbols endpoint."""

    def test_symbols(self, client: TestClient) -> None:
        """Symbols endpoint returns list of symbols."""
        response = client.get("/symbols")

        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert "count" in data
        assert data["count"] == len(data["symbols"])


class TestOptimizeEndpoint:
    """Tests for /api/optimize endpoint."""

    @patch("backend.api.utils.process_portfolio_price_data")
    @patch("backend.api.utils.fetch_portfolio_stock_data")
    def test_optimize_endpoint_returns_all_strategies(
        self,
        mock_fetch,
        mock_process,
        client: TestClient,
        sample_prices_df: pd.DataFrame,
        mock_empty_fetch: dict[str, pd.DataFrame],
    ) -> None:
        """Optimize endpoint returns all three strategy results."""
        mock_fetch.return_value = mock_empty_fetch
        mock_process.return_value = sample_prices_df

        response = client.post(
            "/optimize",
            json={
                "symbols": ["FPT", "HPG", "VNM"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
                "risk_aversion": 1.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "max_sharpe" in data
        assert "min_volatility" in data
        assert "max_utility" in data

        # Each strategy should have weights, expected_return, volatility, sharpe_ratio
        for strategy in ["max_sharpe", "min_volatility", "max_utility"]:
            assert "weights" in data[strategy]
            assert "expected_return" in data[strategy]
            assert "volatility" in data[strategy]
            assert "sharpe_ratio" in data[strategy]


class TestHRPEndpoint:
    """Tests for /api/hrp endpoint."""

    @patch("backend.api.utils.process_portfolio_price_data")
    @patch("backend.api.utils.fetch_portfolio_stock_data")
    def test_hrp_endpoint_returns_weights(
        self,
        mock_fetch,
        mock_process,
        client: TestClient,
        sample_prices_df: pd.DataFrame,
        mock_empty_fetch: dict[str, pd.DataFrame],
    ) -> None:
        """HRP endpoint returns weights dictionary."""
        mock_fetch.return_value = mock_empty_fetch
        mock_process.return_value = sample_prices_df

        response = client.post(
            "/hrp",
            json={
                "symbols": ["FPT", "HPG", "VNM"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "weights" in data
        assert isinstance(data["weights"], dict)


class TestAllocateEndpoint:
    """Tests for /api/allocate endpoint."""

    @patch("backend.api.utils.process_portfolio_price_data")
    @patch("backend.api.utils.fetch_portfolio_stock_data")
    def test_allocate_endpoint_returns_allocation(
        self,
        mock_fetch,
        mock_process,
        client: TestClient,
        sample_prices_df: pd.DataFrame,
        mock_empty_fetch: dict[str, pd.DataFrame],
    ) -> None:
        """Allocate endpoint returns share allocation."""
        mock_fetch.return_value = mock_empty_fetch
        mock_process.return_value = sample_prices_df

        response = client.post(
            "/allocate",
            json={
                "symbols": ["FPT", "HPG", "VNM"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
                "strategy": "max_sharpe",
                "portfolio_value": 10000000,
                "risk_aversion": 1.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "allocation" in data
        assert "leftover" in data
        assert "allocated" in data
        assert data["portfolio_value"] == 10000000

    def test_allocate_endpoint_rejects_invalid_strategy(self, client: TestClient) -> None:
        """Allocate endpoint rejects invalid strategy."""
        response = client.post(
            "/allocate",
            json={
                "symbols": ["FPT", "HPG", "VNM"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
                "strategy": "invalid_strategy",
                "portfolio_value": 10000000,
            },
        )

        assert response.status_code == 422  # Validation error


class TestRiskEndpoint:
    """Tests for /api/risk endpoint."""

    @patch("backend.api.utils.process_portfolio_price_data")
    @patch("backend.api.utils.fetch_portfolio_stock_data")
    def test_risk_endpoint_returns_metrics(
        self,
        mock_fetch,
        mock_process,
        client: TestClient,
        sample_prices_df: pd.DataFrame,
        mock_empty_fetch: dict[str, pd.DataFrame],
    ) -> None:
        """Risk endpoint returns risk metrics."""
        mock_fetch.return_value = mock_empty_fetch
        mock_process.return_value = sample_prices_df

        response = client.post(
            "/risk",
            json={
                "symbols": ["FPT", "HPG", "VNM"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
                "strategy": "max_sharpe",
                "risk_aversion": 1.0,
                "alpha": 0.05,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "profitability" in data
        assert "return_based_risks" in data
        assert "drawdown_based_risks" in data
        assert "risk_adjusted_ratios" in data


class TestErrorHandling:
    """Tests for error handling."""

    @patch("backend.api.utils.fetch_portfolio_stock_data")
    def test_optimize_with_fetch_error(
        self,
        mock_fetch,
        client: TestClient,
    ) -> None:
        """Optimize endpoint handles data fetch errors."""
        from backend.api.exceptions import DataFetchError

        mock_fetch.side_effect = DataFetchError("No data fetched")

        response = client.post(
            "/optimize",
            json={
                "symbols": ["INVALID"],
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
                "risk_aversion": 1.0,
            },
        )

        assert response.status_code == 502  # Bad Gateway