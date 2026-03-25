# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                                # Install/update dependencies
uv run pyopt                           # Run app via CLI entry point
uv run streamlit run app.py            # Run app via ASGI entry point
uvicorn app:app --reload               # Run via external uvicorn
```

When changing dependencies, keep both files in sync:

```bash
# After editing pyproject.toml:
uv lock
uv export --format requirements-txt --no-emit-project > requirements.txt
```

## Architecture

ASGI application using Streamlit 1.55's `st.App` (Starlette backend) with a reusable `backend/` package.

```
app.py                    ← ASGI entry point (st.App + API routes)
streamlit_app.py          ← Streamlit UI frontend (caching + rendering)
pyopt_cli.py              ← CLI wrapper (streamlit run app.py)
backend/
├── services/
│   ├── data_service.py       ← vnstock data fetching (pure Python)
│   └── optimization_service.py ← PyPortfolioOpt logic (pure Python)
└── api/
    └── routes.py             ← Starlette HTTP routes (/api/health, /api/info)
```

**Isolation boundary:** `backend/` has zero Streamlit imports. All `@st.cache_data` wrappers live in `streamlit_app.py` as thin delegators to backend service functions.

**Data flow:** User sidebar inputs → `backend/services/data_service` (vnstock API) → pandas price matrix → `backend/services/optimization_service` (PyPortfolioOpt) → `streamlit_app.py` visualization (matplotlib/altair) + export (riskfolio-lib Excel reports)

**API endpoints:** `/api/health` (service health check), `/api/info` (app metadata + strategies)

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
