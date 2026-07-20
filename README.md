# Return to Fundamentals

Replication materials for the working paper series

Amazon Institute of Value Investing and Applied Data Science

---

## The series

Each paper has its own folder, holding its dataset, its conventions, and the scripts that reproduce every published figure.

The accounting functions are shared across papers and live at the root, so a convention is defined once and applied everywhere.

| Paper | Subject | Folder |
| --- | --- | --- |
| WP 2026.01 | Residual earnings: three Brazilian archetypes | wp01-residual-earnings/ |
| WP 2026.03 | Abnormal earnings growth across the Selic cycle | in preparation |

## Structure

```
src/accounting.py            shared: clean surplus, ROCE, residual earnings
tests/test_accounting.py     thirteen checks over known accounting cases
scripts/demo_re.py           demonstration on synthetic data

wp01-residual-earnings/
    data/canonical.csv       per-share panel: EPS, DPS, BPS by firm-year
    data/data_dictionary.md  variables, sources, units, audit rule
    docs/conventions.md      accounting conventions, stated and justified
    scripts/verify.py        accounting tables, valuations, sensitivity
    scripts/verify_vp.py     value-to-price and building blocks
```

## Shared accounting conventions

Implemented once in src/accounting.py. Papers may add conventions of their own, documented in their folder, but never redefine these.

| Convention | Implementation |
| --- | --- |
| Return on common equity | ROCE_t = CI_t / B_(t-1) — beginning book value |
| Residual earnings | RE_t = CI_t − r · B_(t-1) — charge on opening equity |
| Clean surplus | B_t = B_(t-1) + CI_t − d_t, verified per firm-year |
| Earnings measure | Comprehensive income, owners of the parent |

## Data provenance

Datasets are compiled manually from DFP filings (CVM), consolidated statements, amounts attributable to owners of the parent. Every value carries a filing reference in the compilation workbook. No figure enters a dataset without an audit trail.

## Reproducing WP 2026.01

```bash
pip install pandas pytest
python -m pytest tests/
python wp01-residual-earnings/scripts/verify.py
python wp01-residual-earnings/scripts/verify_vp.py
```

Current status:

- 21 of 21 residual earnings reproduced (beginning book value)
- 21 of 21 ROCE figures matched to the beginning-book-value convention
- 9 of 9 valuation scenarios reproduced, max deviation R$ 0.0007 per share
- Clean surplus verified for every firm-year within R$ 0.004 per share
- 27 of 27 value-to-price figures reproduced across three reference dates
- Building block shares reproduced for all three firms

## Citation

Cite the paper whose materials you use. For WP 2026.01:

```bibtex
@techreport{CoelhoDeAssis2026wp01,
  author      = {Coelho de Assis, Antônio Guilherme},
  title       = {Applying Accounting-Based Pricing Logic to Book Value:
                 Three Brazilian Archetypes},
  institution = {Amazon Institute of Value Investing and Applied Data Science},
  type        = {Return to Fundamentals Working Paper},
  number      = {2026.01},
  year        = {2026},
  address     = {Belém, Pará, Brazil}
}
```

## License

Code is released under the MIT License (LICENSE). Datasets and documentation are released under Creative Commons Attribution 4.0 International (LICENSE-data).

## Disclaimer

These materials are provided for research and educational purposes. They present accounting-based valuation exercises and are not investment advice or a recommendation to buy or sell any security.

## Contact

Amazon Institute of Value Investing and Applied Data Science
Belém, Pará, Brazil
