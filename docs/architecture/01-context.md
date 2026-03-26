# System Context

> C4 Level 1: System Context Diagram

## Overview

PyOpt is a portfolio optimization tool for the Vietnamese stock market. It provides a web-based dashboard for investors and MCP tools for AI assistants like Claude Desktop.

## Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#56524D', 'primaryTextColor': '#1F1916', 'primaryBorderColor': '#2B2523', 'lineColor': '#76706C', 'secondaryColor': '#D4D4D4', 'tertiaryColor': '#E4E4E4'}}}%%

C4Context
    title System Context Diagram - PyOpt Portfolio Optimizer

    Person(user, "User", "Investor seeking portfolio optimization")
    Person(claude, "Claude Desktop", "AI assistant using MCP tools")

    System_Boundary(pyopt, "PyOpt Dashboard") {
        System(streamlit, "Streamlit UI", "Portfolio optimization dashboard")
        System(api, "FastAPI", "REST API with 7 endpoints")
        System(mcp, "MCP Server", "5 MCP tools for Claude")
    }

    System_Ext(vnstock, "vnstock API", "Vietnamese stock market data")
    System_Ext(browser, "Web Browser", "User interface")

    Rel(user, browser, "Uses", "HTTPS")
    Rel(browser, streamlit, "Views dashboard", "HTTP")
    Rel(claude, mcp, "Invokes tools", "MCP/stdio")
    Rel(streamlit, api, "Calls API", "HTTP")
    Rel(mcp, api, "Wraps", "OpenAPI")
    Rel(api, vnstock, "Fetches prices", "HTTP")
```

## System Actors

### Primary Actors

| Actor | Description | Interface |
|-------|-------------|-----------|
| **User** | Vietnamese investor seeking portfolio optimization | Web browser |
| **Claude Desktop** | AI assistant helping users with investment decisions | MCP protocol |

### External Systems

| System | Description | Protocol |
|--------|-------------|----------|
| **vnstock API** | Vietnamese stock market data provider (HOSE, HNX, UPCOM) | HTTP/REST |
| **Web Browser** | User interface for accessing the dashboard | HTTP |

## System Scope

### In Scope

- Portfolio optimization using Modern Portfolio Theory
- Three optimization strategies: Max Sharpe, Min Volatility, Max Utility
- Hierarchical Risk Parity (HRP) optimization
- Discrete share allocation in VND
- Risk metrics calculation (24 metrics)
- Excel report generation
- MCP tools for Claude Desktop integration

### Out of Scope

- Real-time trading execution
- Backtesting with historical strategies
- User authentication and portfolio persistence
- Multi-user support
- Mobile applications