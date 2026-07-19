# Applying Accounting-Based Pricing Logic to Book Value: Three Brazilian Archetypes

**Replication materials for Working Paper 2026.01**
Return to Fundamentals series · Amazon Institute of Value Investing and Applied Data Science

---

## Overview

This repository contains the data, code, and tests behind Working Paper
2026.01. It exists so that any reader can reproduce every figure in the
paper, audit the accounting conventions adopted, and extend the analysis
to additional firms.

The paper applies the residual earnings framework of Penman (2013,
Chapter 5) to three Brazilian listed companies selected as archetypes of
the framework's canonical cases: M. Dias Branco (MDIA3) as Case 1,
residual earnings oscillating around zero; Vivara (VIVA3) as Case 2,
persistent positive residual earnings; and RD Saúde (RADL3) as Case 3,
residual earnings growing with an expanding capital base. The analysis
covers 2021–2025 realized accounting plus two years of explicit forecast,
with continuing value under three growth scenarios.

## What is included

```
data/
    canonical_wp01.csv        per-share panel: EPS, DPS, BPS by firm-year
    data_dictionary.md        variable definitions, sources, units, audit rule
src/
    accounting.py             clean surplus, ROCE and residual earnings functions
tests/
    test_accounting.py        thirteen unit tests over known cases
scripts/
    verify_wp01.py            re-derives the accounting tables and valuations
    verify_vp.py              re-derives value-to-price and building blocks
    demo_re.py                end-to-end demonstration on synthetic data
docs/
    conventions.md            the accounting conventions, stated and justified
```

## Accounting conventions

These conventions are written once, in `src/accounting.py`, and every
figure in the paper derives from them. They cannot drift between tables.

| Convention | Implementation |
| --- | --- |
| Return on common equity | `ROCE_t = CI_t / B_{t-1}` — beginning book value |
| Residual earnings | `RE_t = CI_t − r · B_{t-1}` — capital charge on opening equity |
| Clean surplus | `B_t = B_{t-1} + CI_t − d_t`, verified for every firm-year |
| Earnings measure | Comprehensive income attributable to owners of the parent |
| Required return | 10 percent throughout, per the paper's Section 3.3 |

Penman (2013, Box 5.1, p. 147) presents ROCE on both beginning and
average book value; the beginning-of-period base is used here because it
is the one required for the identity `RE_t = (ROCE_t − r) · B_{t-1}` to
hold, and the one used in the box's own illustration. See
`docs/conventions.md`.

## Data provenance

The canonical dataset was compiled manually from the DFP filings of the
three companies (consolidated statements, amounts attributable to owners
of the parent), as filed with the Comissão de Valores Mobiliários (CVM).
Every value carries a filing reference in the compilation workbook. No
figure enters the dataset without an audit trail, and no table in the
paper contains a number typed by hand.

## Reproducing the results

Requirements: Python 3.10 or later, `pandas`, `pytest`.

```bash
pip install pandas pytest

python -m pytest tests/          # 13 tests over known accounting cases
python scripts/verify_wp01.py    # accounting tables, valuations, sensitivity
python scripts/verify_vp.py      # value-to-price and building block shares
```

`verify_wp01.py` recomputes ROCE under both candidate conventions, all
residual earnings, and the full sensitivity grid, then compares each
figure against the manuscript. Current status:

- 21 of 21 residual earnings reproduced (beginning book value)
- 21 of 21 ROCE figures matched to the beginning-book-value convention
- 9 of 9 valuation scenarios reproduced, maximum deviation R$ 0.0007 per share
- Clean surplus verified for every firm-year within R$ 0.004 per share
- 27 of 27 value-to-price figures reproduced across three reference dates
- Building block shares reproduced for all three firms

## Citation

If you use these materials, please cite the working paper:

```bibtex
@techreport{Assis2026wp01,
  author      = {Assis, Antônio Guilherme Coelho de},
  title       = {The Accounting for Value: Applying Penman's Framework
                 to Three Brazilian Archetypes},
  institution = {Amazon Institute of Value Investing and Applied Data Science},
  type        = {Return to Fundamentals Working Paper},
  number      = {2026.01},
  year        = {2026},
  address     = {Belém, Pará, Brazil}
}
```

## License

Code is released under the MIT License (`LICENSE`). The dataset and
documentation are released under Creative Commons Attribution 4.0
International (`LICENSE-data`).

## Disclaimer

These materials are provided for research and educational purposes. They
present accounting-based valuation exercises and are not investment
advice or a recommendation to buy or sell any security.

## Contact

Amazon Institute of Value Investing and Applied Data Science
Belém, Pará, Brazil
