# Container Architecture

> C4 Level 2: Container Diagram

## Overview

PyOpt runs as a single ASGI application with three logical containers: Streamlit UI, FastAPI backend, and MCP Server. All containers share the same process and backend services.

## Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#56524D', 'primaryTextColor': '#1F1916', 'primaryBorderColor': '#2B2523', 'lineColor': '#76706C', 'secondaryColor': '#D4D4D4', 'tertiaryColor': '#E4E4E4'}}}%%

C4Container
    title Container Diagram - PyOpt Portfolio Optimizer

    Person(user, "User", "Investor")
    Person(claude, "Claude Desktop", "AI assistant")

    System_Boundary(pyopt, "PyOpt Application") {
        Container(streamlit, "Streamlit UI", "Python/Streamlit", "Interactive dashboard with 5 tabs")
        Container(api, "FastAPI", "Python/FastAPI", "REST API with 7 endpoints")
        Container(mcp, "MCP Server", "Python/FastMCP", "5 MCP tools exposed via OpenAPI")

        ContainerDb(services, "Backend Services", "Python", "Data fetching, optimization, risk analysis")
    }

    System_Ext(vnstock, "vnstock API", "Vietnamese stock market data provider")

    Rel(user, streamlit, "Uses", "HTTP/80")
    Rel(claude, mcp, "MCP protocol", "stdio")
    Rel(streamlit, services, "Calls directly", "Python")
    Rel(api, services, "Delegates to", "Python")
    Rel(mcp, api, "Wraps routes", "OpenAPI schema")
    Rel(services, vnstock, "Quote.history()", "HTTP")
```

## Containers

### Streamlit UI

| Property | Value |
|----------|-------|
| **Technology** | Python, Streamlit |
| **Port** | 80 (configurable) |
| **Path** | `/` |
| **Purpose** | Interactive portfolio optimization dashboard |

**Features:**
- 5 tabs: Efficient Frontier & Weights, HRP, Dollars Allocation, Report, Risk Analysis
- Sidebar controls for ticker selection, date range, risk aversion
- Caching via `@st.cache_data`
- Matplotlib charts (efficient frontier, dendrogram, risk plots)
- Altair donut charts (portfolio weights)
- Excel report download

### FastAPI

| Property | Value |
|----------|-------|
| **Technology** | Python, FastAPI |
| **Port** | Same as Streamlit (shared process) |
| **Path** | `/api` |
| **Purpose** | REST API for programmatic access |

**Endpoints:**
- `GET /api/health` — Health check
- `GET /api/info` — App metadata
- `GET /api/symbols` — List stock symbols
- `POST /api/optimize` — Run all 3 strategies
- `POST /api/hrp` — HRP optimization
- `POST /api/allocate` — Discrete allocation
- `POST /api/risk` — Risk metrics

### MCP Server

| Property | Value |
|----------|-------|
| **Technology** | Python, FastMCP |
| **Protocol** | MCP over stdio |
| **Purpose** | Claude Desktop integration |

**MCP Tools (5):**
- `symbols` — List available stock symbols
- `optimize` — Run portfolio optimization
- `hrp` — Run HRP optimization
- `allocate` — Convert weights to shares
- `risk` — Compute risk metrics

### Backend Services

| Service | File | Purpose |
|---------|------|---------|
| **data_service** | `backend/services/data_service.py` | vnstock data fetching |
| **optimization_service** | `backend/services/optimization_service.py` | PyPortfolioOpt integration |
| **risk_service** | `backend/services/risk_service.py` | riskfolio-lib integration |

## Communication Patterns

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| User Browser | Streamlit | HTTP | Dashboard access |
| Claude Desktop | MCP Server | MCP/stdio | Tool invocation |
| Streamlit | Backend Services | Python | Direct function calls |
| FastAPI | Backend Services | Python | Direct function calls |
| MCP Server | FastAPI | OpenAPI | Route discovery |
| Backend Services | vnstock | HTTP | Stock data fetching

## Deployment

Single-process ASGI application:

```bash
# Run locally
uv run pyopt

# Or with uvicorn
uvicorn app:app --reload

# MCP server (separate process)
uv run python server.py
```

**Render.com deployment:**
- Single web service
- Python native runtime with uv
- Port 80 (configurable)