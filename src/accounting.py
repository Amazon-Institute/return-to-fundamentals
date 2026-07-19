"""
accounting.py — Core accounting-based valuation functions.

Return to Fundamentals — Amazon Institute of Value Investing
and Applied Data Science.

Conventions (per Penman, Financial Statement Analysis and Security
Valuation, and the Institute's decision log):

- ROCE uses OPENING book value: ROCE_t = CI_t / B_{t-1}.
- Residual earnings: RE_t = CI_t - r * B_{t-1}.
- Earnings measure: comprehensive income attributable to owners of
  the parent (net income accepted as robustness input).
- Clean surplus: B_t = B_{t-1} + CI_t - d_t, where d_t is net
  distributions to shareholders (dividends + interest on equity +
  buybacks - issuances). d_t > 0 is a net outflow to shareholders.
- Rates are decimals (0.15, never 15).

All functions are pure and operate on scalars or pandas objects.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TOL_DEFAULT = 0.005  # 0.5% relative tolerance for clean surplus checks


# ---------------------------------------------------------------------------
# Clean surplus
# ---------------------------------------------------------------------------

def reconcile_equity(beginning: float, comprehensive_income: float,
                     net_distributions: float, ending: float,
                     tol: float = TOL_DEFAULT) -> dict:
    """Check the clean surplus identity B_t = B_{t-1} + CI_t - d_t.

    Parameters
    ----------
    beginning : opening common shareholders' equity, B_{t-1}
    comprehensive_income : CI_t attributable to owners of the parent
    net_distributions : d_t (dividends + IoE + buybacks - issuances);
        positive = net outflow to shareholders
    ending : reported closing equity, B_t
    tol : relative tolerance (vs. |ending|, floor of 1.0 currency unit)

    Returns
    -------
    dict with implied ending equity, absolute and relative gap, and a
    boolean 'clean' flag. A False flag signals dirty surplus or a data
    error and must be audited before the observation enters the panel.

    Examples
    --------
    >>> r = reconcile_equity(100.0, 10.0, 4.0, 106.0)
    >>> r['clean'], round(r['implied_ending'], 2)
    (True, 106.0)
    >>> r = reconcile_equity(100.0, 10.0, 4.0, 111.0)
    >>> r['clean'], round(r['gap'], 2)
    (False, 5.0)
    """
    implied = beginning + comprehensive_income - net_distributions
    gap = ending - implied
    denom = max(abs(ending), 1.0)
    rel = abs(gap) / denom
    return {
        "implied_ending": implied,
        "gap": gap,
        "relative_gap": rel,
        "clean": bool(rel <= tol),
    }


def reconcile_equity_panel(df: pd.DataFrame,
                           firm: str = "firm", year: str = "year",
                           b: str = "equity", ci: str = "ci",
                           d: str = "net_dist",
                           tol: float = TOL_DEFAULT) -> pd.DataFrame:
    """Vectorised clean surplus check on a firm-year panel.

    Expects one row per firm-year with CLOSING equity in `b`.
    Opening equity is taken as the firm's previous-year closing equity,
    so each firm's first year cannot be checked (flag is <NA>).
    """
    out = df.sort_values([firm, year]).copy()
    out["b_open"] = out.groupby(firm)[b].shift(1)
    out["implied_ending"] = out["b_open"] + out[ci] - out[d]
    out["gap"] = out[b] - out["implied_ending"]
    denom = out[b].abs().clip(lower=1.0)
    out["relative_gap"] = out["gap"].abs() / denom
    out["clean"] = (out["relative_gap"] <= tol).astype("boolean")
    out.loc[out["b_open"].isna(), "clean"] = pd.NA
    return out


# ---------------------------------------------------------------------------
# ROCE and residual earnings
# ---------------------------------------------------------------------------

def roce(comprehensive_income: float, opening_equity: float) -> float:
    """ROCE_t = CI_t / B_{t-1}  (opening book value convention).

    Returns np.nan when opening equity is not strictly positive:
    ROCE has no economic interpretation on zero or negative book value.

    >>> round(roce(24.1, 100.0), 3)
    0.241
    >>> roce(10.0, 0.0)
    nan
    """
    if opening_equity is None or not np.isfinite(opening_equity) \
            or opening_equity <= 0:
        return float("nan")
    return comprehensive_income / opening_equity


def residual_earnings(comprehensive_income: float, opening_equity: float,
                      required_return: float) -> float:
    """RE_t = CI_t - r * B_{t-1}.

    The capital charge is levied on OPENING equity, consistent with the
    ROCE convention. `required_return` is a decimal (0.12, not 12).

    >>> residual_earnings(15.0, 100.0, 0.10)
    5.0
    >>> residual_earnings(8.0, 100.0, 0.10)
    -2.0
    """
    _check_rate(required_return)
    return comprehensive_income - required_return * opening_equity


def residual_earnings_panel(df: pd.DataFrame, r,
                            firm: str = "firm", year: str = "year",
                            b: str = "equity", ci: str = "ci") -> pd.DataFrame:
    """Compute B_{t-1}, ROCE and RE on a firm-year panel.

    `r` may be a scalar (constant hurdle, Specification 1) or the name
    of a column holding a per-year rate (variable hurdle,
    Specification 2, e.g. Selic + fixed premium).

    RE_t = (ROCE_t - r_t) * B_{t-1}: the check column verifies the
    identity against the direct computation to 1e-9.
    """
    out = df.sort_values([firm, year]).copy()
    out["b_open"] = out.groupby(firm)[b].shift(1)
    rate = out[r] if isinstance(r, str) else float(r)
    if not isinstance(r, str):
        _check_rate(rate)
    out["roce"] = out[ci] / out["b_open"].where(out["b_open"] > 0)
    out["re"] = out[ci] - rate * out["b_open"]
    diff = (out["roce"] - rate) * out["b_open"] - out["re"]
    out["re_identity_check"] = (diff.abs() < 1e-9).astype("boolean") \
        .where(diff.notna())
    return out


def _check_rate(r) -> None:
    arr = np.asarray(r, dtype=float)
    if np.any(arr < 0) or np.any(arr > 1):
        raise ValueError(
            "required_return must be a decimal in [0, 1], e.g. 0.15 for "
            "15%. Got a value outside this range — likely a percent/"
            "decimal unit error."
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
