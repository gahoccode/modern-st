"""HTTP API routes for the pyopt application.

Pure Starlette routes — no Streamlit imports. Thin handlers that delegate
to backend.services for any business logic.
"""

from importlib.metadata import PackageNotFoundError, version

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from backend.services.optimization_service import STRATEGY_CHOICES

try:
    APP_VERSION = version("pyopt")
except PackageNotFoundError:
    APP_VERSION = "0.1.0"


async def health(request: Request) -> JSONResponse:
    """GET /api/health — Service health check (idempotent, safe)."""
    return JSONResponse({
        "status": "healthy",
        "app": "pyopt",
        "version": APP_VERSION,
    })


async def info(request: Request) -> JSONResponse:
    """GET /api/info — App metadata and available strategies."""
    return JSONResponse({
        "app": "pyopt",
        "version": APP_VERSION,
        "strategies": STRATEGY_CHOICES,
    })


def get_api_routes() -> list[Route]:
    """Return all API routes for mounting on st.App."""
    return [
        Route("/api/health", health, methods=["GET"]),
        Route("/api/info", info, methods=["GET"]),
    ]
