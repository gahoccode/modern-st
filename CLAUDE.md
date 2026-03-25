# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                                # Install/update dependencies
uv run pyopt                           # Run app (uvicorn on port 8501)
uvicorn app:app --reload               # Run with auto-reload
uv run python server.py                # Run MCP server
```

When changing dependencies, keep both files in sync:

```bash
# After editing pyproject.toml:
uv lock
uv export --format requirements-txt --no-emit-project > requirements.txt
```

## Architecture

Pattern B architecture: FastAPI as root, Streamlit mounted as sub-app. FastMCP auto-exposes API routes as MCP tools.

```
app.py                    ← ASGI entry point (FastAPI root + Streamlit mount)
server.py                 ← MCP server (FastMCP.from_fastapi)
streamlit_app.py          ← Streamlit UI frontend (caching + rendering)
pyopt_cli.py              ← CLI wrapper (streamlit run app.py)
backend/
├── services/
│   ├── data_service.py       ← vnstock data fetching (pure Python)
│   ├── optimization_service.py ← PyPortfolioOpt logic (pure Python)
│   └── risk_service.py        ← riskfolio-lib risk metrics (pure Python)
└── api/
    ├── exceptions.py         ← domain exceptions + HTTP error handlers
    ├── models.py             ← Pydantic request/response models
    ├── utils.py              ← shared data-fetching (get_price_matrix)
    └── routes.py             ← thin FastAPI route handlers + app factory
```

**Isolation boundary:** `backend/` has zero Streamlit imports. All `@st.cache_data` wrappers live in `streamlit_app.py` as thin delegators to backend service functions.

**Data flow:** User sidebar inputs → `backend/services/data_service` (vnstock API) → pandas price matrix → `backend/services/optimization_service` (PyPortfolioOpt) → `streamlit_app.py` visualization (matplotlib/altair) + export (riskfolio-lib Excel reports)

**API endpoints (7 routes, mounted at `/api`):**

| Method | Path | Description | MCP |
|--------|------|-------------|-----|
| `GET` | `/api/health` | Service health check | excluded (internal) |
| `GET` | `/api/info` | App metadata + available strategies | excluded (internal) |
| `GET` | `/api/symbols` | List all available stock symbols | tool |
| `POST` | `/api/optimize` | Run all 3 optimization strategies | tool |
| `POST` | `/api/hrp` | Run Hierarchical Risk Parity optimization | tool |
| `POST` | `/api/allocate` | Convert weights to discrete share counts (VND) | tool |
| `POST` | `/api/risk` | Portfolio risk analysis (24 metrics) | tool |

**MCP server** (`server.py`): `FastMCP.from_fastapi()` auto-converts FastAPI routes into MCP tools via the OpenAPI schema. Routes tagged `internal` are excluded via `mcp.disable(tags={"internal"})`.

**Three optimization strategies** are computed upfront on every run:

- Max Sharpe Ratio (`EfficientFrontier.max_sharpe`)
- Min Volatility (`EfficientFrontier.min_volatility`)
- Max Utility (`EfficientFrontier.max_quadratic_utility`)

A shared radio button (`portfolio_strategy_master`) controls which strategy is used across the Dollars Allocation, Report, and Risk Analysis tabs.

**Five tabs:**

1. Efficient Frontier & Weights — scatter plot of 5,000 random portfolios + weight tables/pie charts
2. Hierarchical Risk Parity — HRPOpt with dendrogram
3. Dollars Allocation — DiscreteAllocation converting weights to VND share counts
4. Report — Riskfolio-lib Excel export to `exports/reports/`
5. Risk Analysis — riskfolio plot_table, plot_drawdown, plot_range

**Caching:** `@st.cache_data` wrappers in `streamlit_app.py` delegate to `backend/services/` pure functions. Cached on `load_stock_symbols()` (max 1 entry) and `fetch_portfolio_stock_data()` (keyed by symbols + date range + interval).

## Key Conventions

- Python 3.10+ with type hints on function signatures
- Earth-tone custom theme defined in `.streamlit/config.toml`
- Prices from vnstock are in thousands; multiply by 1,000 for actual VND values before discrete allocation
- The `pyopt` console script in `pyproject.toml` points to `pyopt_cli:main`, which programmatically invokes `streamlit run`
- UV is the package manager; hatchling is the build backend
- No test suite, linter, or CI pipeline configured yet
- Keep FastAPI routes thin and separate from business logic
- Decouple bussiness logic from framework
- Draw project folder tree for preview before implementing a feature affecting significant architectural change
