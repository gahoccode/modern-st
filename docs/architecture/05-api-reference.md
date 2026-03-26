# API Reference

Complete documentation for all 7 FastAPI endpoints.

## Overview

| Method | Path | MCP Tool | Description |
|--------|------|----------|-------------|
| `GET` | `/api/health` | excluded | Service health check |
| `GET` | `/api/info` | excluded | App metadata |
| `GET` | `/api/symbols` | `symbols` | List stock symbols |
| `POST` | `/api/optimize` | `optimize` | Run all 3 strategies |
| `POST` | `/api/hrp` | `hrp` | HRP optimization |
| `POST` | `/api/allocate` | `allocate` | Discrete allocation |
| `POST` | `/api/risk` | `risk` | Risk metrics |

**Base URL:** `http://localhost:80/api`

---

## Internal Endpoints

These endpoints are excluded from MCP via `mcp.disable(tags={"internal"})`.

### GET /api/health

Health check endpoint for monitoring.

**Request:**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "pyopt",
  "version": "0.1.0"
}
```

**Status Codes:**
- `200 OK` — Service is healthy

---

### GET /api/info

Application metadata and available strategies.

**Request:**
```http
GET /api/info
```

**Response:**
```json
{
  "app": "pyopt",
  "version": "0.1.0",
  "strategies": [
    "Max Sharpe Portfolio",
    "Min Volatility Portfolio",
    "Max Utility Portfolio"
  ]
}
```

**Status Codes:**
- `200 OK` — Success

---

## MCP Tools

These endpoints are exposed as MCP tools for Claude Desktop.

### GET /api/symbols

List all available Vietnamese stock symbols from HOSE, HNX, and UPCOM exchanges.

**MCP Tool:** `symbols`

**Request:**
```http
GET /api/symbols
```

**Response:**
```json
{
  "symbols": [
    "A32",
    "AAM",
    "ABC",
    "... (2000+ symbols)",
    "VNM",
    "VPB",
    "VRE"
  ],
  "count": 2187
}
```

**Status Codes:**
- `200 OK` — Success

---

### POST /api/optimize

Run all three portfolio optimization strategies (Max Sharpe, Min Volatility, Max Utility).

**MCP Tool:** `optimize`

**Request Body:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "risk_aversion": 1.0
}
```

**Schema:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbols` | `array[string]` | Yes | — | Stock ticker symbols |
| `start_date` | `string` | Yes | — | Start date (YYYY-MM-DD) |
| `end_date` | `string` | Yes | — | End date (YYYY-MM-DD) |
| `risk_aversion` | `number` | No | `1.0` | Risk aversion for max_utility (≥0) |

**Response:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "risk_aversion": 1.0,
  "max_sharpe": {
    "weights": {"FPT": 0.45, "HPG": 0.35, "VNM": 0.20},
    "expected_return": 0.182345,
    "volatility": 0.156789,
    "sharpe_ratio": 1.163456
  },
  "min_volatility": {
    "weights": {"FPT": 0.30, "HPG": 0.25, "VNM": 0.45},
    "expected_return": 0.145678,
    "volatility": 0.123456,
    "sharpe_ratio": 1.180234
  },
  "max_utility": {
    "weights": {"FPT": 0.40, "HPG": 0.30, "VNM": 0.30},
    "expected_return": 0.167890,
    "volatility": 0.145678,
    "sharpe_ratio": 1.152345
  }
}
```

**PortfolioResult Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `weights` | `object` | Asset weights (sums to 1.0) |
| `expected_return` | `number` | Annualized expected return |
| `volatility` | `number` | Annualized standard deviation |
| `sharpe_ratio` | `number` | Risk-adjusted return |

**Status Codes:**
- `200 OK` — Success
- `502 Bad Gateway` — vnstock data fetch failed
- `422 Unprocessable Entity` — Invalid price data

---

### POST /api/hrp

Run Hierarchical Risk Parity optimization.

**MCP Tool:** `hrp`

**Request Body:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01"
}
```

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbols` | `array[string]` | Yes | Stock ticker symbols |
| `start_date` | `string` | Yes | Start date (YYYY-MM-DD) |
| `end_date` | `string` | Yes | End date (YYYY-MM-DD) |

**Response:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "weights": {
    "FPT": 0.312,
    "HPG": 0.345,
    "VNM": 0.343
  }
}
```

**Status Codes:**
- `200 OK` — Success
- `502 Bad Gateway` — vnstock data fetch failed
- `422 Unprocessable Entity` — Invalid price data

---

### POST /api/allocate

Convert portfolio weights to discrete share counts in VND.

**MCP Tool:** `allocate`

**Request Body:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "strategy": "max_sharpe",
  "portfolio_value": 100000000,
  "risk_aversion": 1.0
}
```

**Schema:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbols` | `array[string]` | Yes | — | Stock ticker symbols |
| `start_date` | `string` | Yes | — | Start date (YYYY-MM-DD) |
| `end_date` | `string` | Yes | — | End date (YYYY-MM-DD) |
| `strategy` | `string` | Yes | — | One of: `max_sharpe`, `min_volatility`, `max_utility` |
| `portfolio_value` | `number` | Yes | — | Total investment in VND (>0) |
| `risk_aversion` | `number` | No | `1.0` | Risk aversion for max_utility (≥0) |

**Response:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "strategy": "max_sharpe",
  "portfolio_value": 100000000,
  "allocation": {
    "FPT": 150,
    "HPG": 200
  },
  "leftover": 567890.12,
  "allocated": 99432109.88
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `allocation` | `object` | Symbol → share count |
| `leftover` | `number` | Uninvested cash (VND) |
| `allocated` | `number` | Invested amount (VND) |

**Status Codes:**
- `200 OK` — Success
- `502 Bad Gateway` — vnstock data fetch failed
- `422 Unprocessable Entity` — Invalid price data

---

### POST /api/risk

Compute comprehensive risk metrics for a portfolio.

**MCP Tool:** `risk`

**Request Body:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "strategy": "max_sharpe",
  "risk_aversion": 1.0,
  "alpha": 0.05
}
```

**Schema:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbols` | `array[string]` | Yes | — | Stock ticker symbols |
| `start_date` | `string` | Yes | — | Start date (YYYY-MM-DD) |
| `end_date` | `string` | Yes | — | End date (YYYY-MM-DD) |
| `strategy` | `string` | Yes | — | One of: `max_sharpe`, `min_volatility`, `max_utility` |
| `risk_aversion` | `number` | No | `1.0` | Risk aversion for max_utility (≥0) |
| `alpha` | `number` | No | `0.05` | Significance level for VaR/CVaR (0<α<1) |

**Response:**
```json
{
  "symbols": ["FPT", "HPG", "VNM"],
  "strategy": "max_sharpe",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "alpha": 0.05,
  "profitability": {
    "mean_return": 0.182345,
    "cagr": 0.156789,
    "mar": 0.0,
    "alpha": 0.05
  },
  "return_based_risks": {
    "std_dev": 0.156789,
    "mad": 0.123456,
    "semi_deviation": 0.112345,
    "flpm": 0.001234,
    "slpm": 0.002345,
    "var": 0.234567,
    "cvar": 0.345678,
    "evar": 0.289012,
    "tail_gini": 0.312345,
    "rlvar": 0.267890,
    "worst_realization": 0.456789,
    "skewness": -0.234567,
    "kurtosis": 3.456789
  },
  "drawdown_based_risks": {
    "ulcer_index": 0.089012,
    "avg_drawdown": 0.056789,
    "dar": 0.234567,
    "cdar": 0.312345,
    "edar": 0.289012,
    "rldar": 0.267890,
    "max_drawdown": 0.456789
  },
  "risk_adjusted_ratios": {
    "std_dev": 1.163456,
    "mad": 1.478901,
    "semi_deviation": 1.623456,
    "...": "..."
  }
}
```

**Risk Metrics (24 total):**

| Category | Metrics |
|----------|---------|
| **Profitability** | mean_return, cagr, mar, alpha |
| **Return-based** | std_dev, mad, semi_deviation, flpm, slpm, var, cvar, evar, tail_gini, rlvar, worst_realization, skewness, kurtosis |
| **Drawdown-based** | ulcer_index, avg_drawdown, dar, cdar, edar, rldar, max_drawdown |
| **Risk-adjusted** | Ratios calculated as (mean_return - mar) / risk |

**Status Codes:**
- `200 OK` — Success
- `502 Bad Gateway` — vnstock data fetch failed
- `422 Unprocessable Entity` — Invalid price data

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Error message description"
}
```

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| `502` | `DataFetchError` | vnstock API failure or empty response |
| `422` | `ProcessingError` | No valid price data after processing |
| `422` | `ValidationError` | Invalid request body |
| `500` | `PyoptError` | Internal server error |

---

## Usage Examples

### cURL

```bash
# Get symbols
curl http://localhost:80/api/symbols

# Optimize portfolio
curl -X POST http://localhost:80/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["FPT", "HPG"], "start_date": "2024-01-01", "end_date": "2025-01-01"}'

# Get risk metrics
curl -X POST http://localhost:80/api/risk \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["FPT", "HPG"], "start_date": "2024-01-01", "end_date": "2025-01-01", "strategy": "max_sharpe"}'
```

### Python (requests)

```python
import requests

# Optimize portfolio
response = requests.post(
    "http://localhost:80/api/optimize",
    json={
        "symbols": ["FPT", "HPG", "VNM"],
        "start_date": "2024-01-01",
        "end_date": "2025-01-01",
        "risk_aversion": 1.0,
    }
)
result = response.json()
print(result["max_sharpe"]["weights"])
```

### Claude Desktop (MCP)

Once configured in `claude_desktop_config.json`, Claude can invoke tools:

```
User: What are the optimal weights for FPT, HPG, and VNM stocks?

Claude: [calls optimize tool]
{
  "symbols": ["FPT", "HPG", "VNM"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "risk_aversion": 1.0
}

Claude: Based on the optimization, the Max Sharpe portfolio recommends:
- FPT: 45%
- HPG: 35%
- VNM: 20%
```