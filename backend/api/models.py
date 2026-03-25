"""Pydantic request and response models for the pyopt API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.services.optimization_service import PortfolioResult

Strategy = Literal["max_sharpe", "min_volatility", "max_utility"]


class PortfolioBaseRequest(BaseModel):
    """Shared fields for all portfolio-related requests."""

    symbols: list[str] = Field(..., description="Stock ticker symbols (e.g. ['FPT', 'HPG'])")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")


class OptimizeRequest(PortfolioBaseRequest):
    """Request body for portfolio optimization."""

    risk_aversion: float = Field(1.0, ge=0, description="Risk aversion parameter for max-utility")


class HRPRequest(PortfolioBaseRequest):
    """Request body for Hierarchical Risk Parity optimization."""


class AllocateRequest(PortfolioBaseRequest):
    """Request body for discrete share allocation."""

    strategy: Strategy = Field(..., description="Optimization strategy to allocate from")
    portfolio_value: float = Field(..., gt=0, description="Total portfolio value in VND")
    risk_aversion: float = Field(1.0, ge=0, description="Risk aversion (used by max_utility)")


class RiskRequest(PortfolioBaseRequest):
    """Request body for portfolio risk analysis."""

    strategy: Strategy = Field(..., description="Optimization strategy to analyze")
    risk_aversion: float = Field(1.0, ge=0, description="Risk aversion (used by max_utility)")
    alpha: float = Field(0.05, gt=0, lt=1, description="Significance level for VaR/CVaR/etc.")


class PortfolioResultResponse(BaseModel):
    """JSON-serializable representation of a single optimization result."""

    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float

    @classmethod
    def from_domain(cls, result: PortfolioResult) -> PortfolioResultResponse:
        """Convert a service-layer PortfolioResult dataclass to an API response model."""
        return cls(
            weights=result.weights,
            expected_return=round(result.expected_return, 6),
            volatility=round(result.volatility, 6),
            sharpe_ratio=round(result.sharpe_ratio, 6),
        )
