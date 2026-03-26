# ADR-001: FastAPI as Root ASGI Application

## Status

Accepted

## Context

The application needs to serve both a web-based dashboard (Streamlit) and a REST API (FastAPI). We need to decide which framework serves as the root ASGI application and how the other is integrated.

Options:
1. Streamlit as root, FastAPI as separate service
2. FastAPI as root, Streamlit mounted as sub-app
3. Separate processes with reverse proxy

## Decision

**FastAPI serves as the root ASGI application**, with Streamlit mounted as a sub-app at the root path `/`.

```python
# app.py
from fastapi import FastAPI
from streamlit.starlette import App as StreamlitApp

streamlit_app = StreamlitApp("streamlit_app.py")
app = FastAPI(lifespan=streamlit_app.lifespan())
app.mount("/api", api)      # FastAPI routes
app.mount("/", streamlit_app)  # Streamlit UI
```

## Consequences

### Positive

- **Single process deployment** — No need for separate servers or reverse proxy
- **Clean API routing** — FastAPI handles `/api/*` natively
- **MCP compatibility** — FastMCP can introspect the FastAPI OpenAPI schema
- **Shared lifespan** — Both apps share the same event loop and resources

### Negative

- **Startup coupling** — Streamlit must initialize before FastAPI can serve requests
- **Port sharing** — Both apps compete for the same port
- **Error propagation** — Errors in Streamlit can crash the entire application

## Alternatives Considered

### Streamlit as Root (Rejected)

Streamlit's `App` class doesn't support mounting other ASGI apps. We would need a separate FastAPI process and reverse proxy configuration.

**Why rejected:** Increases deployment complexity. Requires Nginx/Traefik for routing.

### Separate Processes (Rejected)

Run Streamlit and FastAPI as separate processes with a reverse proxy.

**Why rejected:**
- Requires infrastructure orchestration
- Two processes to manage and monitor
- Increased memory footprint

## References

- [FastAPI Advanced User Guide - Sub Applications](https://fastapi.tiangolo.com/advanced/advanced-sub-applications/)
- [Streamlit Starlette Integration](https://docs.streamlit.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)