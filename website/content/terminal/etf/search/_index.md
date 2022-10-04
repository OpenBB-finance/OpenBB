```text
usage: ln -n NAME [NAME ...] [-s {sa,fd}] [-d DESCRIPTION [DESCRIPTION ...]] [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Search for an ETF by name or description. Using either FinanceDatabase or Stockanalysis.com as the source for the name. And only FinanceDatabase for the description.

````
optional arguments:
  -n NAME [NAME ...], --name NAME [NAME ...]
                        Name to look for ETFs (default: None)
  -d DESCRIPTION [DESCRIPTION ...], --description DESCRIPTION [DESCRIPTION ...]
                        Name to look for ETFs (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 5)
  --source {sa,fd}      Data source to select from (default: None)
````

Sample output:

```
2022 Jan 18, 23:49 (✨) /etf/ $ search -n energy -l 10
╒══════╤═══════════════════════════════════════════════════════╤═══════════════════════════════════╤════════════════════════════╤════════════════════╕
│      │ Name                                                  │ Family                            │ Category                   │   Total Assets [M] │
╞══════╪═══════════════════════════════════════════════════════╪═══════════════════════════════════╪════════════════════════════╪════════════════════╡
│ XLE  │ Energy Select Sector SPDR Fund                        │ SPDR State Street Global Advisors │ Equity Energy              │           23081.07 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ VDE  │ Vanguard Energy Index Fund ETF Shares                 │ Vanguard                          │ Equity Energy              │            5883.56 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ ICLN │ iShares Global Clean Energy ETF                       │ iShares                           │ Miscellaneous Sector       │            5811.92 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ QCLN │ First Trust NASDAQ Clean Edge Green Energy Index Fund │ First Trust                       │ Miscellaneous Sector       │            2680.65 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ PBW  │ Invesco WilderHill Clean Energy ETF                   │ Invesco                           │ Miscellaneous Sector       │            2200.06 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ EMLP │ First Trust North American Energy Infrastructure Fund │ First Trust                       │ Energy Limited Partnership │            1858.28 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ IXC  │ iShares Global Energy ETF                             │ iShares                           │ Equity Energy              │            1312.18 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ ACES │ ALPS Clean Energy ETF                                 │ ALPS                              │ Equity Energy              │             970.75 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ FENY │ Fidelity MSCI Energy Index ETF                        │ Fidelity Investments              │ Equity Energy              │             889.72 │
├──────┼───────────────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────┼────────────────────┤
│ MLPX │ Global X MLP & Energy Infrastructure ETF              │ Global X Funds                    │ Energy Limited Partnership │             714.83 │
╘══════╧═══════════════════════════════════════════════════════╧═══════════════════════════════════╧════════════════════════════╧════════════════════╛
```


```
2022 Jan 18, 23:52 (✨) /etf/ $ search -d 3X -l 10
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
