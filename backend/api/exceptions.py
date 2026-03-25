"""Domain exceptions and FastAPI exception handlers for the pyopt API."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class PyoptError(Exception):
    """Base exception for pyopt domain errors."""

    status_code: int = 500


class DataFetchError(PyoptError):
    """Raised when stock data cannot be fetched or is empty (upstream failure)."""

    status_code: int = 502


class ProcessingError(PyoptError):
    """Raised when price data processing produces no valid results."""

    status_code: int = 422


async def pyopt_error_handler(request: Request, exc: PyoptError) -> JSONResponse:
    """Convert any PyoptError to a JSON response with the appropriate status code."""
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc)})
