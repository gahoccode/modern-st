**Streamlit 1.53** (released late January 2026) introduced an experimental ASGI entry point, replacing its old Tornado server with **Starlette** support.[1]

## What Changed in Streamlit 1.53+

Streamlit's server was previously built on **Tornado**, which was intentionally locked away from developers. With 1.53, Streamlit introduced `st.App` — an experimental ASGI-compatible entry point that enables custom HTTP routes, middleware, lifecycle hooks, and seamless integration with Python web frameworks like **FastAPI** and **Starlette**.[1]

To enable Starlette mode, set this config in `.streamlit/config.toml`:

```toml
[server]
useStarlette = true
```

You then create an `app.py` (ASGI entry point) referencing your `streamlit_app.py` (UI), then run via `streamlit run app.py` or `uvicorn app:app --reload`.[1]

## `st.App` Constructor

```python
from streamlit.starlette import App

App(
    script_path: str | Path,
    *,
    lifespan: Callable[[App], AbstractAsyncContextManager[...]] | None = None,
    routes: Sequence[BaseRoute] | None = None,
    middleware: Sequence[Middleware] | None = None,
    exception_handlers: Mapping[Any, ExceptionHandler] | None = None,
    debug: bool = False,
)
```

**Parameters:**
- `script_path` — Path to the main Streamlit UI script (absolute or relative)
- `lifespan` — Optional async context manager for startup/shutdown hooks
- `routes` — Additional Starlette routes (cannot override reserved `/_stcore/` prefixes)
- `middleware` — Custom middleware stack
- `exception_handlers` — Custom exception handlers
- `debug` — Enable Starlette debug mode

## Example Architecture

```bash
my-app/
├── app.py              # ASGI entry point (st.App + routes)
├── streamlit_app.py    # Streamlit UI frontend
├── backend/
│   ├── services/       # Business logic (framework-agnostic)
│   └── api/            # Starlette/FastAPI routes
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

## Deployment Modes

1. **`streamlit run app.py`** — Auto-detects `st.App`, uses internal uvicorn
2. **`uvicorn app:app --reload`** — Direct ASGI server (external uvicorn)
3. **Mount on FastAPI** — `fastapi_app.mount("/dashboard", streamlit_app)` with `.lifespan()` method

## What You Can Now Do

- **Add custom HTTP routes** — pass Starlette `Route` objects via the `routes` parameter on `App()`[1]
- **Mount on a FastAPI app** — use `app.lifespan()` to delegate lifecycle management to a parent FastAPI/Starlette app[1]
- **Starlette WebSockets** — real-time data streams pushed to Streamlit components without triggering reruns[1]
- **Middleware** — add cookie handling, IP whitelisting, security headers, CORS, rate limiting[1]
- **Lifespan hooks** — pre-warm ML models or DB connections before the Streamlit UI loads[1]

## Code Examples

### Pattern 1: Standalone with custom routes

```python
# app.py — ASGI entry point with Starlette routes
from streamlit.starlette import App
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

async def health(request: Request) -> JSONResponse:
    return {"status": "healthy"}

app = App(
    "streamlit_app.py",
    routes=[Route("/api/health", health, methods=["GET"])],
)
```

Run: `streamlit run app.py` or `uvicorn app:app --reload`

### Pattern 2: With lifespan hooks

```python
# app.py — Pre-warm resources before UI loads
from contextlib import asynccontextmanager
from streamlit.starlette import App

@asynccontextmanager
async def lifespan(app):
    print("Starting up — loading model...")
    yield {"model": load_model()}
    print("Shutting down...")

app = App("streamlit_app.py", lifespan=lifespan)
```

### Pattern 3: Mount on FastAPI

```python
# app.py — Streamlit mounted inside a FastAPI app
from fastapi import FastAPI
from streamlit.starlette import App

streamlit_app = App("streamlit_app.py")
fastapi_app = FastAPI(lifespan=streamlit_app.lifespan())
fastapi_app.mount("/dashboard", streamlit_app)

# Run: uvicorn app:fastapi_app --reload
```

## Dependencies

Install the Starlette extras:

```bash
pip install "streamlit[starlette]"
```

This adds: `starlette`, `uvicorn`, `anyio`, `h11`, `itsdangerous`, `python-multipart`, `websockets`.

## Sources

[1] Streamlit over Starlette/FastAPI is a Game-Changer - YouTube https://www.youtube.com/watch?v=UJawnUviOlw
[2] Release Notes - FastAPI https://fastapi.tiangolo.com/release-notes/
[3] Release notes - Streamlit Docs https://docs.streamlit.io/develop/quick-reference/release-notes
[4] 2026 release notes - Streamlit Docs https://docs.streamlit.io/develop/quick-reference/release-notes/2026
[5] Version 1.55.0 - Official Announcements - Streamlit https://discuss.streamlit.io/t/version-1-55-0/120960
