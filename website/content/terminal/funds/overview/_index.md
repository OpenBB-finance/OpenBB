```
usage: overview [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Show overview of funds from selected country.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of search results to show (default: 20)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```

Sample usage:
```
2022 Feb 15, 03:50 (✨) /funds/ $ overview
                                                                      Fund overview for United States
┌──────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┬────────┬────────┬────────┬──────────┬─────────────┐
│ name                                                             │ full_name                                         │ symbol │ last   │ change │ currency │ Assets (1B) │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard 500 Index Fund Admiral Shares                           │ Vanguard 500 Index Admiral                        │ VFIAX  │ 406.79 │ -0.37% │ USD      │ 429.58      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Fidelity® 500 Index Fund                                         │ Fidelity 500 Index Institutional Prem             │ FXAIX  │ 152.90 │ -0.38% │ USD      │ 387.09      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund Admiral Shares            │ Vanguard Total Stock Market Index Admiral         │ VTSAX  │ 108.10 │ -0.40% │ USD      │ 321.58      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund Institutional Plus Shares │ Vanguard Total Stock Market Index Instl Plus      │ VSMPX  │ 202.76 │ -0.40% │ USD      │ 289.35      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Fidelity® Government Money Market Fund                           │ Fidelity Government Money Market Fund             │ SPAXX  │ 1.00   │ 0%     │ USD      │ 230.36      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund Institutional Shares      │ Vanguard Total Stock Market Index I               │ VITSX  │ 108.12 │ -0.40% │ USD      │ 230.26      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Fidelity® Government Cash Reserves                               │ Fidelityֲ® Government Cash Reserves                │ FDRXX  │ 1.00   │ 0%     │ USD      │ 226.13      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total International Stock Index Fund Investor Shares    │ Vanguard Total International Stock Index Inv      │ VGTSX  │ 19.75  │ -0.70% │ USD      │ 188.28      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Institutional Index Fund Institutional Plus Shares      │ Vanguard Institutional Index Instl Pl             │ VIIIX  │ 375.32 │ -0.38% │ USD      │ 167.72      │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Bond Market Ii Index Fund Investor Shares         │ Vanguard Total Bond Market II Index Fund Investor │ VTBIX  │ 10.59  │ -0.56% │ USD      │ 134.58      │
└──────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────┴────────┴────────┴────────┴──────────┴─────────────┘
```
