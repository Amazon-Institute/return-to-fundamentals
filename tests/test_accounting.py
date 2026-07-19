"""Tests for src/accounting.py — known cases, edge cases, panel checks."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
import pytest

from accounting import (reconcile_equity, reconcile_equity_panel,
                        roce, residual_earnings, residual_earnings_panel)


# ---------------- clean surplus, scalar ----------------

def test_clean_case_dividend():
    r = reconcile_equity(100, 10, 4, 106)
    assert r["clean"] and abs(r["gap"]) < 1e-12

def test_clean_case_injection():
    # F = -20: shareholder injects capital
    r = reconcile_equity(100, 10, -20, 130)
    assert r["clean"]

def test_clean_case_loss_with_injection():
    r = reconcile_equity(100, -8, -12, 104)
    assert r["clean"]

def test_dirty_surplus_flagged():
    r = reconcile_equity(100, 10, 4, 111)
    assert not r["clean"] and r["gap"] == pytest.approx(5.0)

def test_telescoping_four_periods():
    """C4 = C0 + sum(I) - sum(F): the worked example (100 -> 125)."""
    c, I, F = 100.0, [10, 10, -8, 12], [4, -20, 0, 15]
    for i, f in zip(I, F):
        c = c + i - f
    assert c == pytest.approx(100 + sum(I) - sum(F)) == pytest.approx(125.0)


# ---------------- ROCE ----------------

def test_roce_opening_book_value():
    assert roce(24.1, 100.0) == pytest.approx(0.241)

def test_roce_undefined_on_nonpositive_equity():
    assert np.isnan(roce(10.0, 0.0))
    assert np.isnan(roce(10.0, -50.0))


# ---------------- residual earnings ----------------

def test_re_positive_and_negative():
    assert residual_earnings(15, 100, 0.10) == pytest.approx(5.0)
    assert residual_earnings(8, 100, 0.10) == pytest.approx(-2.0)

def test_re_zero_when_roce_equals_r():
    b, r = 200.0, 0.12
    ci = r * b
    assert residual_earnings(ci, b, r) == pytest.approx(0.0)

def test_unit_error_rejected():
    with pytest.raises(ValueError):
        residual_earnings(15, 100, 12)  # 12 instead of 0.12


# ---------------- panel ----------------

def _panel():
    return pd.DataFrame({
        "firm": ["A"] * 4 + ["B"] * 4,
        "year": [2022, 2023, 2024, 2025] * 2,
        "equity": [100, 106, 136, 128, 50, 55, 61, 60],
        "ci":     [np.nan, 10, 10, -8, np.nan, 8, 9, 2],
        "net_dist": [np.nan, 4, -20, 0, np.nan, 3, 3, 3],
        "selic":  [0.1375, 0.1175, 0.1225, 0.15] * 2,
    })

def test_panel_clean_surplus():
    out = reconcile_equity_panel(_panel())
    checked = out[out["clean"].notna()]
    assert bool(checked["clean"].all())
    assert out["clean"].isna().sum() == 2  # first year of each firm

def test_panel_re_constant_hurdle():
    out = residual_earnings_panel(_panel(), r=0.10)
    row = out[(out.firm == "A") & (out.year == 2023)].iloc[0]
    assert row["roce"] == pytest.approx(0.10)          # 10 / 100
    assert row["re"] == pytest.approx(0.0)             # ROCE == r
    assert bool(out["re_identity_check"].dropna().all())

def test_panel_re_variable_hurdle():
    out = residual_earnings_panel(_panel(), r="selic")
    row = out[(out.firm == "A") & (out.year == 2023)].iloc[0]
    assert row["re"] == pytest.approx(10 - 0.1175 * 100)
    assert bool(out["re_identity_check"].dropna().all())
