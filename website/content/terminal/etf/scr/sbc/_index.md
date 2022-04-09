```text
usage: sbc [-c CATEGORY [CATEGORY ...]] [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Search by category [Source: FinanceDatabase/StockAnalysis.com]

```
optional arguments:
  -c CATEGORY [CATEGORY ...], --category CATEGORY [CATEGORY ...]
                        Category to look for (default: None)
  -l LIMIT, --limit LIMIT
                        Limit of ETFs to display (default: 5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 04:30 (✨) /etf/scr/ $ sbc Communications
                                                   ETFs by Category and Total Assets
┌──────┬───────────────────────────────────────────────────────┬───────────────────────────────────┬────────────────┬──────────────────┐
│      │ Name                                                  │ Family                            │ Category       │ Total Assets [M] │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────┼──────────────────┤
│ XLC  │ Communication Services Select Sector SPDR Fund        │ SPDR State Street Global Advisors │ Communications │ 13497.92         │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────┼──────────────────┤
│ VOX  │ Vanguard Communication Services Index Fund ETF Shares │ Vanguard                          │ Communications │ 3716.34          │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────┼──────────────────┤
│ FIVG │ Defiance 5G Next Gen Connectivity ETF                 │ Defiance ETFs                     │ Communications │ 1210.04          │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────┼──────────────────┤
│ FCOM │ Fidelity MSCI Communication Services Index ETF        │ Fidelity Investments              │ Communications │ 723.48           │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────┼──────────────────┤
│ IYZ  │ iShares U.S. Telecommunications ETF                   │ iShares                           │ Communications │ 409.20           │
└──────┴───────────────────────────────────────────────────────┴───────────────────────────────────┴────────────────┴──────────────────┘
```
