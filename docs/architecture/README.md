# Architecture Documentation

This directory contains comprehensive architecture documentation for PyOpt, following the [Arc42](https://arc42.org/) template.

## Contents

### System Diagrams

| Document | Description |
|----------|-------------|
| [01-context.md](01-context.md) | System context diagram showing boundaries and external systems |
| [02-container.md](02-container.md) | Container architecture (Streamlit, FastAPI, MCP) |
| [03-component.md](03-component.md) | Component breakdown of backend services |
| [04-data-flow.md](04-data-flow.md) | Data flow from user input to visualization |
| [05-api-reference.md](05-api-reference.md) | Complete API documentation with schemas |

### Diagrams (Mermaid)

| Diagram | Description |
|---------|-------------|
| [diagrams/context.mmd](diagrams/context.mmd) | C4 Context diagram |
| [diagrams/container.mmd](diagrams/container.mmd) | C4 Container diagram |
| [diagrams/component.mmd](diagrams/component.mmd) | C4 Component diagram |

### Architecture Decision Records

| ADR | Title |
|-----|-------|
| [000-template.md](adr/000-template.md) | ADR template |
| [001-fastapi-as-root.md](adr/001-fastapi-as-root.md) | FastAPI as root ASGI app |
| [002-streamlit-mount.md](adr/002-streamlit-mount.md) | Streamlit mounted as sub-app |
| [003-mcp-exposure.md](adr/003-mcp-exposure.md) | MCP exposure via FastMCP |

## Quick Reference

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Streamlit | Dashboard UI |
| API | FastAPI | REST endpoints |
| MCP | FastMCP | Claude Desktop integration |
| Optimization | PyPortfolioOpt | Mean-variance optimization |
| Risk | riskfolio-lib | Risk metrics & reports |
| Data | vnstock | Vietnamese stock data |

### Mount Points

| Path | Handler | Description |
|------|---------|-------------|
| `/` | Streamlit | Dashboard UI |
| `/api` | FastAPI | REST API |

### Endpoints

| Method | Path | MCP Tool |
|--------|------|----------|
| `GET` | `/api/health` | excluded |
| `GET` | `/api/info` | excluded |
| `GET` | `/api/symbols` | symbols |
| `POST` | `/api/optimize` | optimize |
| `POST` | `/api/hrp` | hrp |
| `POST` | `/api/allocate` | allocate |
| `POST` | `/api/risk` | risk |