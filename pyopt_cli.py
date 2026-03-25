"""CLI entry point for the pyopt application."""

import uvicorn


def main() -> None:
    """Launch the pyopt app via uvicorn."""
    uvicorn.run("app:app", host="0.0.0.0", port=8501)


if __name__ == "__main__":
    main()
