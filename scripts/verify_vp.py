import pandas as pd
V0 = {"MDIA3":{0.0:24.2027,0.01:24.2001,0.02:24.1968},"VIVA3":{0.0:31.3074,0.01:33.2289,0.02:35.6308},"RADL3":{0.0:9.4243,0.01:9.9334,0.02:10.5697}}
ANCHOR = {"MDIA3":(24.3014,-0.0772),"VIVA3":(12.55,3.0359),"RADL3":(4.443,0.816)}
DATES = ["30 Dec 2025","31 Mar 2026","14 May 2026"]
PRICE = {"MDIA3":[23.96,23.01,19.93],"VIVA3":[33.24,25.91,22.60],"RADL3":[23.37,23.45,19.49]}
PUB = {"MDIA3":{0.0:[1.010,1.052,1.214],0.01:[1.010,1.052,1.214],0.02:[1.010,1.052,1.214]},"VIVA3":{0.0:[0.942,1.208,1.385],0.01:[1.000,1.283,1.470],0.02:[1.072,1.375,1.577]},"RADL3":{0.0:[0.403,0.402,0.484],0.01:[0.425,0.424,0.510],0.02:[0.452,0.451,0.542]}}
rows = []
for f in V0:
    for g in (0.0, 0.01, 0.02):
        for i, d in enumerate(DATES):
            c = V0[f][g] / PRICE[f][i]
            p = PUB[f][g][i]
            rows.append({"firm": f, "g": g, "date": d, "price": PRICE[f][i], "computed": round(c,3), "paper": p, "match": abs(c-p) <= 0.002})
vp = pd.DataFrame(rows)
print(vp.to_string(index=False))
print("V/P cells reproduced:", int(vp["match"].sum()), "of", len(vp))
print()
for f, (B, PVRE) in ANCHOR.items():
    P = PRICE[f][2]
    spec = P - B - PVRE
    print(f"{f}: book {B/P*100:.1f}%  PV(RE) {PVRE/P*100:.1f}%  speculative {spec/P*100:.1f}%  (R$ {spec:.2f})")
B = ANCHOR["MDIA3"][0]
print(f"MDIA3: price is {(1 - PRICE[chr(77)+chr(68)+chr(73)+chr(65)+chr(51)][2]/B)*100:.1f} percent below verified book value.")
