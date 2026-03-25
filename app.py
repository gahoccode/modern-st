"""ASGI entry point for the pyopt Streamlit application.

Uses Streamlit's experimental st.App (Starlette backend) to serve the
Streamlit UI with custom API routes.

Run with:
    streamlit run app.py
    uvicorn app:app --reload
"""

from streamlit.starlette import App

from backend.api.routes import get_api_routes

app = App("streamlit_app.py", routes=get_api_routes())
