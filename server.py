"""Expose the FastAPI backend as an MCP server via FastMCP."""

from fastmcp import FastMCP

from backend.api.routes import api

mcp = FastMCP.from_fastapi(app=api)
mcp.disable(tags={"internal"})

if __name__ == "__main__":
    mcp.run()
