"""
demo_re.py — End-to-end demonstration of the WP pipeline on a
synthetic three-firm panel shaped like the canonical dataset.

Run:  python scripts/demo_re.py

Steps: load -> clean surplus audit -> ROCE and residual earnings under
a constant hurdle (Specification 1) and a Selic-linked hurdle
(Specification 2) -> summary table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
from accounting import reconcile_equity_panel, residual_earnings_panel

pd.set_option("display.width", 120)

# Synthetic panel (structure of the canonical dataset; NOT real data)
panel = pd.DataFrame({
    "firm":   ["ALFA3"]*5 + ["BETA3"]*5 + ["GAMA3"]*5,
    "year":   list(range(2021, 2026)) * 3,
    "equity": [1000, 1080, 1170, 1230, 1330,
               500, 540, 575, 600, 640,
               800, 830, 845, 850, 858],
    "ci":     [None, 160, 175, 150, 190,
               None, 70, 75, 65, 80,
               None, 55, 40, 30, 33],
    "net_dist": [None, 80, 85, 90, 90,
                 None, 30, 40, 40, 40,
                 None, 25, 25, 25, 25],
    "selic":  [0.0925, 0.1375, 0.1175, 0.1225, 0.15] * 3,
})
panel["hurdle_spec2"] = panel["selic"] + 0.03  # risk-free + fixed premium

print("=" * 70)
print("1. Clean surplus audit")
print("=" * 70)
cs = reconcile_equity_panel(panel)
print(cs[["firm", "year", "equity", "implied_ending", "gap", "clean"]]
      .to_string(index=False))
n_fail = int((cs["clean"] == False).sum())  # noqa: E712
print(f"\nViolations above tolerance: {n_fail}")

print("\n" + "=" * 70)
print("2. ROCE and RE — Specification 1 (constant hurdle, r = 12%)")
print("=" * 70)
s1 = residual_earnings_panel(panel, r=0.12)
print(s1[["firm", "year", "b_open", "roce", "re"]]
      .dropna().round(3).to_string(index=False))

print("\n" + "=" * 70)
print("3. ROCE and RE — Specification 2 (Selic + 300 bps)")
print("=" * 70)
s2 = residual_earnings_panel(panel, r="hurdle_spec2")
print(s2[["firm", "year", "hurdle_spec2", "roce", "re"]]
      .dropna().round(3).to_string(index=False))

print("\n" + "=" * 70)
print("4. Benchmark effect: RE(spec1) - RE(spec2) = (r2 - r1) * B_open")
print("=" * 70)
cmp = s1[["firm", "year", "b_open"]].copy()
cmp["re_spec1"] = s1["re"]
cmp["re_spec2"] = s2["re"]
cmp["diff"] = cmp["re_spec1"] - cmp["re_spec2"]
cmp["check"] = (panel["hurdle_spec2"] - 0.12) * s1["b_open"]
cmp = cmp.dropna()
assert (cmp["diff"] - cmp["check"]).abs().max() < 1e-6
print(cmp.round(2).to_string(index=False))
print("\nIdentity verified: the gap between specifications is purely "
      "the benchmark effect on opening capital.")
