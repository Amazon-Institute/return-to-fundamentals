# Data Dictionary — Canonical Dataset

One row per firm-year. Manually compiled from DFP filings (CVM),
consolidated statements, amounts attributable to owners of the parent.
Currency: BRL thousands unless noted. Rates: decimals (0.15 = 15%).

| Column      | Definition                                                    | Source                     | Unit     |
|-------------|---------------------------------------------------------------|----------------------------|----------|
| firm        | B3 ticker, main ON class (e.g. VIVA3)                         | —                          | text     |
| year        | Fiscal year (calendar)                                        | DFP                        | YYYY     |
| ref_date    | Balance sheet date                                            | DFP                        | ISO date |
| equity      | Closing common shareholders' equity, owners of the parent     | DFP — Balanço, PL          | BRL '000 |
| ni          | Net income, owners of the parent                              | DFP — DRE                  | BRL '000 |
| ci          | Comprehensive income, owners of the parent                    | DFP — DRA                  | BRL '000 |
| dividends   | Dividends declared + interest on equity (JCP), gross          | DFP — DMPL                 | BRL '000 |
| buybacks    | Treasury share repurchases                                    | DFP — DMPL                 | BRL '000 |
| issuances   | Capital increases / share issuances                           | DFP — DMPL                 | BRL '000 |
| net_dist    | dividends + buybacks − issuances (d_t; >0 = outflow)          | computed                   | BRL '000 |
| shares      | Weighted-average shares, split/bonus adjusted                 | DFP notes                  | '000     |
| price       | Closing price at ref_date                                     | B3                         | BRL      |
| selic       | Selic target, year-end                                        | BCB series 432             | decimal  |

Audit rule: every value carries a filing page reference in the
compilation workbook. No manual number enters the dataset without an
audit trail. Clean surplus is verified per firm-year by
`reconcile_equity_panel`; failures are documented (dirty surplus items
or data errors) before the observation is used.
