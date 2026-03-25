"""ASGI entry point — FastAPI as root, Streamlit mounted as sub-app.

Run with:
    uvicorn app:app --reload
    uv run pyopt
"""

from fastapi import FastAPI
from streamlit.starlette import App as StreamlitApp

from backend.api.routes import api

streamlit_app = StreamlitApp("streamlit_app.py")

app = FastAPI(lifespan=streamlit_app.lifespan())
app.mount("/api", api)
app.mount("/", streamlit_app)
