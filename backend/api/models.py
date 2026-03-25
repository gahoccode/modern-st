"""Pydantic request and response models for the pyopt API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.services.optimization_service import PortfolioResult

Strategy = Literal["max_sharpe", "min_volatility", "max_utility"]


class OptimizeRequest(BaseModel):
    """Request body for portfolio optimization."""

    symbols: list[str] = Field(..., description="Stock ticker symbols (e.g. ['FPT', 'HPG'])")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    risk_aversion: float = Field(1.0, ge=0, description="Risk aversion parameter for max-utility")


class HRPRequest(BaseModel):
    """Request body for Hierarchical Risk Parity optimization."""

    symbols: list[str] = Field(..., description="Stock ticker symbols")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")


class AllocateRequest(BaseModel):
    """Request body for discrete share allocation."""

    symbols: list[str] = Field(..., description="Stock ticker symbols")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    strategy: Strategy = Field(..., description="Optimization strategy to allocate from")
    portfolio_value: float = Field(..., gt=0, description="Total portfolio value in VND")
    risk_aversion: float = Field(1.0, ge=0, description="Risk aversion (used by max_utility)")


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
