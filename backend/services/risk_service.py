"""Risk analysis service using riskfolio-lib.

Framework-agnostic — no Streamlit imports. Computes the same metrics as
rp.plot_table but returns them as a plain dict instead of a matplotlib figure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from riskfolio.src import RiskFunctions as rk  # noqa: N813
from scipy import stats

T_FACTOR = 252
INI_DAYS = 1
DAYS_PER_YEAR = 252


def compute_risk_metrics(
    returns: pd.DataFrame,
    weights: dict[str, float],
    mar: float = 0.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    kappa: float = 0.30,
    solver: str = "CLARABEL",
) -> dict:
    """Compute portfolio risk metrics matching riskfolio's plot_table output.

    Args:
        returns: Asset returns DataFrame (n_samples x n_assets).
        weights: Portfolio weights keyed by asset symbol.
        mar: Minimum acceptable return (daily, not annualized).
        alpha: Significance level for VaR, CVaR, etc.
        a_sim: Number of CVaRs to approximate Tail Gini.
        kappa: Deformation parameter for RLVaR/RLDaR (0-1).
        solver: CVXPY solver for power cone programming.

    Returns:
        Dict with profitability, return-based risks, drawdown-based risks,
        and risk-adjusted ratios.
    """
    w_df = pd.DataFrame.from_dict(weights, orient="index", columns=["weight"])
    mu = returns.mean()
    cov = returns.cov()
    days = (returns.index[-1] - returns.index[0]).days + INI_DAYS

    x = (returns.to_numpy() @ w_df.to_numpy()).flatten()

    mean_return = float((mu @ w_df).to_numpy().item() * T_FACTOR)
    cagr = float(np.power(np.prod(1 + x), DAYS_PER_YEAR / days) - 1)

    sqrt_t = T_FACTOR**0.5

    return_risks = {
        "std_dev": float(np.sqrt(w_df.T @ cov @ w_df).to_numpy().item() * sqrt_t),
        "mad": float(rk.MAD(x) * sqrt_t),
        "semi_deviation": float(rk.SemiDeviation(x) * sqrt_t),
        "flpm": float(rk.LPM(x, MAR=mar, p=1) * sqrt_t),
        "slpm": float(rk.LPM(x, MAR=mar, p=2) * sqrt_t),
        "var": float(rk.VaR_Hist(x, alpha=alpha) * sqrt_t),
        "cvar": float(rk.CVaR_Hist(x, alpha=alpha) * sqrt_t),
        "evar": float(rk.EVaR_Hist(x, alpha=alpha)[0] * sqrt_t),
        "tail_gini": float(rk.TG(x, alpha=alpha, a_sim=a_sim) * sqrt_t),
        "rlvar": float(rk.RLVaR_Hist(x, alpha=alpha, kappa=kappa, solver=solver) * sqrt_t),
        "worst_realization": float(rk.WR(x) * sqrt_t),
        "skewness": float(stats.skew(x, bias=False)),
        "kurtosis": float(stats.kurtosis(x, bias=False)),
    }

    drawdown_risks = {
        "ulcer_index": float(rk.UCI_Abs(x)),
        "avg_drawdown": float(rk.ADD_Abs(x)),
        "dar": float(rk.DaR_Abs(x)),
        "cdar": float(rk.CDaR_Abs(x, alpha=alpha)),
        "edar": float(rk.EDaR_Abs(x, alpha=alpha)[0]),
        "rldar": float(rk.RLDaR_Abs(x, alpha=alpha, kappa=kappa, solver=solver)),
        "max_drawdown": float(rk.MDD_Abs(x)),
    }

    annualized_mar = mar * T_FACTOR
    risk_adjusted = {}
    for key, val in {**return_risks, **drawdown_risks}.items():
        if key in ("skewness", "kurtosis") or val == 0:
            continue
        risk_adjusted[key] = round((mean_return - annualized_mar) / val, 6)

    return {
        "profitability": {
            "mean_return": round(mean_return, 6),
            "cagr": round(cagr, 6),
            "mar": round(annualized_mar, 6),
            "alpha": alpha,
        },
        "return_based_risks": {k: round(v, 6) for k, v in return_risks.items()},
        "drawdown_based_risks": {k: round(v, 6) for k, v in drawdown_risks.items()},
        "risk_adjusted_ratios": risk_adjusted,
    }
