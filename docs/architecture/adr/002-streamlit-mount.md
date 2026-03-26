# ADR-002: Streamlit Mounted as Sub-Application

## Status

Accepted

## Context

Streamlit needs to coexist with FastAPI in a single ASGI application. Streamlit provides a Starlette-compatible `App` class that can be mounted, but we need to decide:
1. Where to mount it (path)
2. How to handle lifespan events
3. How to share code between UI and API

## Decision

**Mount Streamlit at root path `/` using the Starlette adapter**, with FastAPI at `/api`:

```python
# app.py
streamlit_app = StreamlitApp("streamlit_app.py")
app = FastAPI(lifespan=streamlit_app.lifespan())
app.mount("/api", api)
app.mount("/", streamlit_app)
```

**Key choices:**
- Streamlit at `/` (default path, no URL prefix)
- FastAPI at `/api` (clear API namespace)
- Shared lifespan via `streamlit_app.lifespan()`

## Consequences

### Positive

- **Clean URLs** — Users access `http://host/` for dashboard
- **API separation** — `/api/*` clearly distinguishes API routes
- **Single entry point** — `uvicorn app:app` runs everything
- **Shared services** — Both UI and API use the same backend services

### Negative

- **Route ordering** — Mount order matters (more specific paths first)
- **Static file conflicts** — Streamlit's static files at `/static/*` could conflict
- **WebSocket handling** — Streamlit uses WebSockets for real-time updates

## Implementation Details

### Mount Order

FastAPI must be mounted **before** Streamlit:

```python
app.mount("/api", api)      # ✓ Correct order
app.mount("/", streamlit_app)
```

If reversed, `/api/*` requests would be caught by Streamlit.

### Shared Lifespan

Streamlit's lifespan manager handles:
- Session initialization
- WebSocket connections
- File watcher (in dev mode)

```python
app = FastAPI(lifespan=streamlit_app.lifespan())
```

### Code Sharing

Both UI and API import from `backend/services/`:

```python
# streamlit_app.py
from backend.services.optimization_service import compute_optimizations

# backend/api/routes.py
from backend.services.optimization_service import compute_optimizations
```

## Alternatives Considered

### Streamlit at `/dashboard` (Rejected)

Mount Streamlit at a non-root path.

**Why rejected:**
- Users expect dashboard at root URL
- Breaks Streamlit's internal URL assumptions

### iframe Embedding (Rejected)

Run Streamlit separately and embed in FastAPI-served HTML.

**Why rejected:**
- Requires separate process
- CORS issues
- Poor user experience

## References

- [Streamlit Starlette App](https://docs.streamlit.io/)
- [FastAPI Mounting](https://fastapi.tiangolo.com/advanced/advanced-sub-applications/)
- [ASGI Lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html)