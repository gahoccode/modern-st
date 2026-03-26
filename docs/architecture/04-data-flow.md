# Data Flow

> Data transformation pipeline from user input to visualization

## Overview

Data flows from user input through the Streamlit UI (frontend package), to backend services, and finally to visualization or export. The architecture separates concerns: frontend handles caching and UI, services handle business logic.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER INPUT (frontend/sidebar.py)                                            │
│ symbols: ["REE", "HPG", "FPT"]                                               │
│ start_date: "2024-01-01"                                                     │
│ end_date: "2025-01-01"                                                       │
│ risk_aversion: 1.0                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ FRONTEND LAYER (frontend/caching.py)                                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @st.cache_data                                                       │    │
│  │ fetch_portfolio_stock_data(tuple(symbols), start, end, "1D")        │    │
│  │ → Delegates to backend/services/data_service                        │    │
│  │ → Returns: dict[str, DataFrame]                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ process_portfolio_price_data(all_historical_data)                   │    │
│  │ → Delegates to backend/services/data_service                        │    │
│  │ → Returns: DataFrame (prices, indexed by date)                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DATA SERVICE (backend/services/data_service.py)                              │
│                                                                              │
│  vnstock.Quote(symbol).history(start, end, interval)                        │
│  → HTTP request to vnstock API                                               │
│  → Returns: DataFrame with time, close, volume, etc.                        │
│                                                                              │
│  process_portfolio_price_data()                                              │
│  → Concatenates close prices                                                │
│  → Returns: DataFrame with columns = symbols, index = dates                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ RETURNS CALCULATION                                                          │
│                                                                              │
│  compute_returns(prices_df)                                                  │
│  → prices_df.pct_change().dropna()                                           │
│  → Returns: DataFrame with daily returns                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ OPTIMIZATION SERVICE (backend/services/optimization_service.py)              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ compute_optimizations(prices_df, risk_aversion)                      │    │
│  │                                                                       │    │
│  │   mu = expected_returns.mean_historical_return(prices_df)            │    │
│  │   cov_matrix = risk_models.sample_cov(prices_df)                     │    │
│  │                                                                       │    │
│  │   EfficientFrontier(mu, cov_matrix)                                  │    │
│  │     .max_sharpe() → weights_max_sharpe                               │    │
│  │     .min_volatility() → weights_min_vol                              │    │
│  │     .max_quadratic_utility() → weights_max_utility                   │    │
│  │                                                                       │    │
│  │   Returns: OptimizationResults                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ compute_hrp(returns)                                                 │    │
│  │   HRPOpt(returns=returns).optimize()                                 │    │
│  │   Returns: HRPResult (weights + hrp_instance)                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ VISUALIZATION / EXPORT (frontend/tabs/)                                      │
│                                                                              │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐   │
│  │ Efficient Frontier│  │ HRP Dendrogram    │  │ Risk Analysis         │   │
│  │ (efficient_       │  │ (hrp.py)          │  │ (risk_analysis.py)    │   │
│  │ frontier.py)      │  │                   │  │                       │   │
│  │                   │  │                   │  │                       │   │
│  │ • 5000 portfolios │  │ • Cluster tree    │  │ • plot_table()        │   │
│  │ • Scatter plot    │  │ • Asset linkage   │  │ • plot_drawdown()     │   │
│  │ • Sharpe coloring │  │                   │  │ • plot_range()        │   │
│  └───────────────────┘  └───────────────────┘  └───────────────────────┘   │
│                                                                              │
│  ┌───────────────────┐  ┌───────────────────┐                               │
│  │ Weights Donut     │  │ Excel Report      │                               │
│  │ (components.py)   │  │ (report.py)       │                               │
│  │                   │  │                   │                               │
│  │ • Altair chart    │  │ • .xlsx download  │                               │
│  │ • Strategy split  │  │ • Performance     │                               │
│  └───────────────────┘  └───────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Caching Strategy

Streamlit's `@st.cache_data` is used to avoid redundant API calls and computations. All cache decorators are isolated in `frontend/caching.py`.

| Cached Function | Cache Key | Max Entries |
|-----------------|-----------|-------------|
| `load_stock_symbols()` | None (singleton) | 1 |
| `fetch_portfolio_stock_data()` | symbols tuple, dates, interval | Unlimited |
| `cached_compute_optimizations()` | prices_df hash, risk_aversion | Unlimited |
| `cached_compute_hrp()` | returns hash | Unlimited |

**Why this works:**
- `tuple(sorted(symbols))` ensures consistent cache keys
- DataFrame hashing works for small datasets
- No cache on `process_portfolio_price_data()` (transform is cheap)
- Cache wrappers delegate to backend services (zero Streamlit deps in backend)

## Price Data Transformation

```
vnstock API Response (per symbol):
┌────────────┬───────┬────────┬───────┐
│ time       │ open  │ close  │ volume│
├────────────┼───────┼────────┼───────┤
│ 2024-01-02 │ 52000 │ 52500  │ 15000 │
│ 2024-01-03 │ 53000 │ 52800  │ 12000 │
└────────────┴───────┴────────┴───────┘

                    │
                    ▼ process_portfolio_price_data()

Combined Price Matrix:
┌────────────┬───────┬───────┬───────┐
│ time       │ REE   │ HPG   │ FPT   │
├────────────┼───────┼───────┼───────┤
│ 2024-01-02 │ 52500 │ 28500 │ 95000 │
│ 2024-01-03 │ 52800 │ 28800 │ 95200 │
└────────────┴───────┴───────┴───────┘

Note: Prices are in thousands (multiply by 1000 for actual VND)
```

## Discrete Allocation Flow

```
Portfolio Weights (from optimization):
┌───────┬────────┐
│ REE   │ 0.35   │
│ HPG   │ 0.40   │
│ FPT   │ 0.25   │
└───────┴────────┘
        │
        ▼ compute_discrete_allocation(weights, prices_df, portfolio_value=100_000_000)

Latest Prices (actual VND):
┌───────┬─────────────┐
│ REE   │ 52,500,000  │
│ HPG   │ 28,500,000  │
│ FPT   │ 95,000,000  │
└───────┴─────────────┘
        │
        ▼ DiscreteAllocation.greedy_portfolio()

Allocation Result:
┌───────┬────────┬──────────────┬────────────────┐
│ REE   │ 1 share│ 52,500,000   │ 52.5%          │
│ HPG   │ 1 share│ 28,500,000   │ 28.5%          │
└───────┴────────┴──────────────┴────────────────┘
Leftover: 19,000,000 VND (19%)
```

## Error Handling

| Stage | Error Type | Handling |
|-------|------------|----------|
| Data fetch | `DataFetchError` (502) | vnstock API failure |
| Processing | `ProcessingError` (422) | Empty price matrix |
| Optimization | ValueError | Invalid parameters |
| UI | `st.error()` | User-friendly message |