"""FastAPI routes for the pyopt application.

Thin handlers that delegate to backend services. Request/response models
live in models.py; shared data-fetching logic lives in utils.py.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter, FastAPI

from backend.api.exceptions import PyoptError, pyopt_error_handler
from backend.api.models import (
    AllocateRequest,
    HRPRequest,
    OptimizeRequest,
    PortfolioResultResponse,
    RiskRequest,
)
from backend.api.utils import get_price_matrix
from backend.services.data_service import DEFAULT_SYMBOLS, compute_returns, load_stock_symbols
from backend.services.optimization_service import (
    STRATEGY_CHOICES,
    compute_discrete_allocation,
    compute_hrp,
    compute_optimizations,
    compute_single_strategy,
)
from backend.services.risk_service import compute_risk_metrics

try:
    APP_VERSION = version("pyopt")
except PackageNotFoundError:
    APP_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/health", tags=["internal"], summary="Service health check")
async def health() -> dict:
    """Return service health status, app name, and version."""
    return {"status": "healthy", "app": "pyopt", "version": APP_VERSION}


@router.get("/info", tags=["internal"], summary="App metadata")
async def info() -> dict:
    """Return app metadata and available optimization strategies."""
    return {"app": "pyopt", "version": APP_VERSION, "strategies": STRATEGY_CHOICES}


@router.get("/symbols", summary="List available stock symbols")
async def symbols() -> dict:
    """List all Vietnamese stock symbols available for optimization."""
    try:
        symbol_list = load_stock_symbols()
    except Exception:
        symbol_list = DEFAULT_SYMBOLS
    return {"symbols": symbol_list, "count": len(symbol_list)}


@router.post("/optimize", summary="Run portfolio optimization")
async def optimize(body: OptimizeRequest) -> dict:
    """Run Max Sharpe, Min Volatility, and Max Utility optimizations on the given symbols."""
    prices_df = get_price_matrix(body.symbols, body.start_date, body.end_date)
    results = compute_optimizations(prices_df, body.risk_aversion)
    return {
        "symbols": body.symbols,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "risk_aversion": body.risk_aversion,
        "max_sharpe": PortfolioResultResponse.from_domain(results.max_sharpe).model_dump(),
        "min_volatility": PortfolioResultResponse.from_domain(results.min_volatility).model_dump(),
        "max_utility": PortfolioResultResponse.from_domain(results.max_utility).model_dump(),
    }


@router.post("/hrp", summary="Run HRP optimization")
async def hrp(body: HRPRequest) -> dict:
    """Run Hierarchical Risk Parity optimization on the given symbols."""
    prices_df = get_price_matrix(body.symbols, body.start_date, body.end_date)
    returns = compute_returns(prices_df)
    hrp_result = compute_hrp(returns)
    return {
        "symbols": body.symbols,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "weights": hrp_result.weights,
    }


@router.post("/allocate", summary="Allocate shares from optimization")
async def allocate(body: AllocateRequest) -> dict:
    """Convert optimization weights into discrete share counts in VND."""
    prices_df = get_price_matrix(body.symbols, body.start_date, body.end_date)
    opt_result = compute_single_strategy(prices_df, body.strategy, body.risk_aversion)
    result = compute_discrete_allocation(opt_result.weights, prices_df, body.portfolio_value)
    return {
        "symbols": body.symbols,
        "strategy": body.strategy,
        "portfolio_value": body.portfolio_value,
        "allocation": result.allocation,
        "leftover": round(result.leftover, 2),
        "allocated": round(body.portfolio_value - result.leftover, 2),
    }


@router.post("/risk", summary="Run portfolio risk analysis")
async def risk(body: RiskRequest) -> dict:
    """Compute risk metrics for a given strategy.

    Returns return-based, drawdown-based, and risk-adjusted ratios.
    """
    prices_df = get_price_matrix(body.symbols, body.start_date, body.end_date)
    opt_result = compute_single_strategy(prices_df, body.strategy, body.risk_aversion)
    returns = compute_returns(prices_df)
    metrics = compute_risk_metrics(returns, opt_result.weights, alpha=body.alpha)
    return {
        "symbols": body.symbols,
        "strategy": body.strategy,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "alpha": body.alpha,
        **metrics,
    }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

api = FastAPI(
    title="PyOpt API",
    version=APP_VERSION,
    description="Vietnamese stock portfolio optimization API",
)
api.include_router(router)
api.add_exception_handler(PyoptError, pyopt_error_handler)
