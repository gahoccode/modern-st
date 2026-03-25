"""Domain exceptions and FastAPI exception handlers for the pyopt API."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class DataFetchError(Exception):
    """Raised when stock data cannot be fetched or is empty."""


class ProcessingError(Exception):
    """Raised when price data processing produces no valid results."""


async def data_fetch_handler(request: Request, exc: DataFetchError) -> JSONResponse:
    """Convert DataFetchError to a 400 JSON response."""
    return JSONResponse(status_code=400, content={"error": str(exc)})


async def processing_handler(request: Request, exc: ProcessingError) -> JSONResponse:
    """Convert ProcessingError to a 400 JSON response."""
    return JSONResponse(status_code=400, content={"error": str(exc)})
