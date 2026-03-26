# ADR-003: MCP Exposure via FastMCP

## Status

Accepted

## Context

We want to enable Claude Desktop integration via the Model Context Protocol (MCP). MCP allows AI assistants to invoke tools programmatically.

Options:
1. Manual MCP tool definitions (boilerplate)
2. FastMCP auto-generation from FastAPI OpenAPI schema
3. Custom MCP server with duplicate route logic

## Decision

**Use FastMCP to auto-expose FastAPI routes as MCP tools** via OpenAPI introspection:

```python
# server.py
from fastmcp import FastMCP
from backend.api.routes import api

mcp = FastMCP.from_fastapi(app=api)
mcp.disable(tags={"internal"})  # Exclude health/info endpoints

if __name__ == "__main__":
    mcp.run()
```

**Key choices:**
- Zero boilerplate — FastMCP generates tool definitions from OpenAPI
- Internal tag exclusion — `health` and `info` endpoints hidden from MCP
- stdio transport — Claude Desktop communicates via stdin/stdout

## Consequences

### Positive

- **Zero boilerplate** — No manual tool definitions needed
- **Single source of truth** — OpenAPI schema drives both API and MCP
- **Automatic type inference** — Request/response types preserved
- **Easy maintenance** — Adding API routes automatically adds MCP tools

### Negative

- **OpenAPI dependency** — Requires well-typed FastAPI routes
- **Limited customization** — Tool descriptions come from route docstrings
- **Debugging complexity** — MCP errors can be hard to trace

## Exposed Tools

| MCP Tool | FastAPI Endpoint | Description |
|----------|------------------|-------------|
| `symbols` | `GET /api/symbols` | List stock symbols |
| `optimize` | `POST /api/optimize` | Run all 3 strategies |
| `hrp` | `POST /api/hrp` | HRP optimization |
| `allocate` | `POST /api/allocate` | Discrete allocation |
| `risk` | `POST /api/risk` | Risk metrics |

**Excluded (internal tag):**
- `GET /api/health`
- `GET /api/info`

## Configuration

Add to Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pyopt": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/modern-st"
    }
  }
}
```

## Alternatives Considered

### Manual MCP Definitions (Rejected)

Define each tool manually with `@mcp.tool()` decorators.

```python
@mcp.tool()
def optimize(symbols: list[str], start_date: str, end_date: str) -> dict:
    # Duplicate logic from FastAPI route
    ...
```

**Why rejected:**
- High boilerplate
- Duplicate definitions to maintain
- Easy to get out of sync

### Custom MCP Server (Rejected)

Separate MCP server with its own route handlers.

**Why rejected:**
- Code duplication
- Two places to update for changes
- Higher maintenance burden

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Integration](https://docs.anthropic.com/claude/docs/mcp)