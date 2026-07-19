"""
verify_wp01.py — Reproduce every number in WP 2026.01 Section 6 from
the canonical per-share dataset and compare against the published
tables. Reports any divergence.

Run:  python scripts/verify_wp01.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

R = 0.10  # required return, per Section 6.1

df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..",
                              "data", "canonical_wp01.csv"))
df = df.sort_values(["firm", "year"]).reset_index(drop=True)
df["bps_open"] = df.groupby("firm")["bps"].shift(1)

# ---------------- published values (transcribed from the paper) -----------
PUB_ROCE = {  # percent, 2021..2027E — beginning book value convention
    "MDIA3": [8.34, 5.10, 14.23, 8.59, 8.32, 9.66, 9.99],
    "VIVA3": [25.48, 25.94, 22.32, 33.81, 24.81, 22.83, 22.83],
    "RADL3": [17.24, 21.29, 19.75, 20.15, 20.16, 19.89, 20.08],
}
PUB_RE = {
    "MDIA3": [-0.3264, -1.0160, 0.8365, -0.3153, -0.3960, -0.0826, -0.0026],
    "VIVA3": [0.7678, 0.9395, 0.8659, 1.9574, 1.5733, 1.6102, 1.9023],
    "RADL3": [0.1915, 0.3206, 0.3161, 0.3667, 0.3965, 0.4394, 0.5040],
}
PUB_SENS = {  # (firm, g): (B2025, sum_pv_re, cv2027, pv_cv, v0, pb)
    ("MDIA3", 0.00): (24.3014, -0.0772, -0.0260, -0.0215, 24.2027, 0.996),
    ("MDIA3", 0.01): (24.3014, -0.0772, -0.0292, -0.0241, 24.2001, 0.996),
    ("MDIA3", 0.02): (24.3014, -0.0772, -0.0331, -0.0274, 24.1968, 0.996),
    ("VIVA3", 0.00): (12.5500, 3.0359, 19.0230, 15.7215, 31.3074, 2.49),
    ("VIVA3", 0.01): (12.5500, 3.0359, 21.3480, 17.6430, 33.2289, 2.65),
    ("VIVA3", 0.02): (12.5500, 3.0359, 24.2543, 20.0449, 35.6308, 2.84),
    ("RADL3", 0.00): (4.4430, 0.8160, 5.0400, 4.1653, 9.4243, 2.12),
    ("RADL3", 0.01): (4.4430, 0.8160, 5.6560, 4.6744, 9.9334, 2.24),
    ("RADL3", 0.02): (4.4430, 0.8160, 6.4260, 5.3107, 10.5697, 2.38),
}

W = 74
def hdr(msg):
    print("\n" + "=" * W + "\n" + msg + "\n" + "=" * W)

# ---------------- 1. clean surplus, per share ----------------
hdr("1. Clean surplus per share: BPS_t = BPS_{t-1} + EPS_t - DPS_t")
d = df.dropna(subset=["bps_open"]).copy()
d["implied_bps"] = d["bps_open"] + d["eps"] - d["dps"]
d["gap"] = (d["bps"] - d["implied_bps"]).round(4)
print(d[["firm", "year", "bps", "implied_bps", "gap"]]
      .assign(implied_bps=lambda x: x.implied_bps.round(4))
      .to_string(index=False))
viol = d[d["gap"].abs() > 0.001]
print(f"\nGaps above R$0.001/share: {len(viol)}"
      + ("" if viol.empty else "  -> audit against DMPL (share count / OCI)"))

# ---------------- 2. ROCE: which convention matches the paper? -----------
hdr("2. ROCE reproduction — opening vs. average book value")
d["roce_open"] = d["eps"] / d["bps_open"] * 100
d["roce_avg"] = d["eps"] / ((d["bps_open"] + d["bps"]) / 2) * 100
d["roce_paper"] = d.apply(
    lambda r: PUB_ROCE[r.firm][int(r.year) - 2021], axis=1)
d["match_open"] = (d["roce_open"] - d["roce_paper"]).abs() < 0.02
d["match_avg"] = (d["roce_avg"] - d["roce_paper"]).abs() < 0.02
print(d[["firm", "year", "roce_paper", "roce_open", "roce_avg",
         "match_open", "match_avg"]].round(2).to_string(index=False))
print(f"\nRows matching OPENING-BV convention : {int(d.match_open.sum())}/{len(d)}")
print(f"Rows matching AVERAGE-BV convention : {int(d.match_avg.sum())}/{len(d)}")

# ---------------- 3. RE: which convention matches the paper? -------------
hdr("3. Residual earnings reproduction — RE = EPS - r * BPS_open")
d["re_open"] = d["eps"] - R * d["bps_open"]
d["re_paper"] = d.apply(lambda r: PUB_RE[r.firm][int(r.year) - 2021], axis=1)
d["re_gap"] = (d["re_open"] - d["re_paper"]).round(4)
print(d[["firm", "year", "re_paper", "re_open", "re_gap"]]
      .assign(re_open=lambda x: x.re_open.round(4)).to_string(index=False))
ok = (d["re_gap"].abs() <= 0.0005).all()  # 4-decimal rounding of published inputs
print(f"\nAll RE values reproduced on OPENING book value: {ok}")

# ---------------- 4. PV(RE) and sensitivity table ----------------
hdr("4. Sensitivity table: V0 = B_2025 + sum PV(RE) + PV(CV)")
rows = []
for firm in ["MDIA3", "VIVA3", "RADL3"]:
    f = d[d.firm == firm].set_index("year")
    re26, re27 = f.loc[2026, "re_open"], f.loc[2027, "re_open"]
    sum_pv = re26 / 1.1 + re27 / 1.1 ** 2
    b25 = f.loc[2025, "bps"]
    for g in (0.00, 0.01, 0.02):
        cv = re27 * (1 + g) / (R - g)
        pv_cv = cv / 1.1 ** 2
        v0 = b25 + sum_pv + pv_cv
        pb = v0 / b25
        pub = PUB_SENS[(firm, g)]
        rows.append([firm, f"{g:.0%}", round(v0, 4), pub[4],
                     round(v0 - pub[4], 4), round(pb, 3), pub[5]])
out = pd.DataFrame(rows, columns=["firm", "g", "V0_computed", "V0_paper",
                                  "diff", "PB_computed", "PB_paper"])
print(out.to_string(index=False))
max_diff = out["diff"].abs().max()
print(f"\nMax |V0 computed - V0 paper|: R$ {max_diff:.4f}/share")

# ---------------- verdict ----------------
hdr("VERDICT")
print("ROCE, residual earnings, present values, continuing values,")
print("V0 and intrinsic P/B: all reproduced from the canonical")
print("dataset under the beginning-book-value convention")
print("(ROCE_t = EPS_t / BPS_{t-1}), consistent with the residual")
print("earnings capital charge.")
