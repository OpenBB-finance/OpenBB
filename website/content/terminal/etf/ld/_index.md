
```text
usage: ld [-d DESCRIPTION [DESCRIPTION ...]] [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Search for an ETF by description using either FinanceDatabase or StockAnalysis as the source. [Source: FinanceDatabase/StockAnalysis.com]

```
optional arguments:
  -d DESCRIPTION [DESCRIPTION ...], --description DESCRIPTION [DESCRIPTION ...]
                        Name to look for ETFs (default: None)
  -l LIMIT, --limit LIMIT
                        Limit of ETFs to display (default: 5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Sample output:

```
2022 Jan 18, 23:52 (✨) /etf/ $ ld 3X -l 10
╒══════╤═════════════════════════════════════════════════════╤══════════════╤═══════════════════════════╤════════════════════╕
│      │ Name                                                │ Family       │ Category                  │   Total Assets [M] │
╞══════╪═════════════════════════════════════════════════════╪══════════════╪═══════════════════════════╪════════════════════╡
│ TQQQ │ ProShares UltraPro QQQ                              │ ProShares    │ Trading--Leveraged Equity │           11266.33 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ UPRO │ ProShares UltraPro S&P500                           │ ProShares    │ Trading--Leveraged Equity │            2007.68 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ SQQQ │ ProShares UltraPro Short QQQ                        │ ProShares    │ Trading--Inverse Equity   │            1515.03 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ UDOW │ ProShares UltraPro Dow30                            │ ProShares    │ Trading--Leveraged Equity │             878.03 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ SPXU │ ProShares UltraPro Short S&P500                     │ ProShares    │ Trading--Inverse Equity   │             510.83 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ NRGU │ MicroSectors U.S. Big Oil Index 3X Leveraged ETNs   │ Microsectors │                           │             448.66 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ URTY │ ProShares UltraPro Russell2000                      │ ProShares    │ Trading--Leveraged Equity │             444.82 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ SDOW │ ProShares UltraPro Short Dow30                      │ ProShares    │ Trading--Inverse Equity   │             380.26 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ SRTY │ ProShares UltraPro Short Russell2000                │ ProShares    │ Trading--Inverse Equity   │             110.51 │
├──────┼─────────────────────────────────────────────────────┼──────────────┼───────────────────────────┼────────────────────┤
│ BNKU │ MicroSectors U.S. Big Banks Index 3X Leveraged ETNs │ Microsectors │ Trading--Leveraged Equity │              86.87 │
╘══════╧═════════════════════════════════════════════════════╧══════════════╧═══════════════════════════╧════════════════════╛ 
```