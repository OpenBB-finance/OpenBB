```
usage: pick [-t OPTION] [-h]
```

Select the status of the underlying: long, short, none.

```
optional arguments:
  -t {long,short,none}, --type {long,short,none}
                        Choose what you would like to do with the underlying asset (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 09:25 (✨) /stocks/options/payoff/ $ pick -t long

2022 Feb 16, 09:25 (✨) /stocks/options/payoff/ $ ?
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Stocks - Options - Payoff ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                                                              │
│ Ticker: TSLA                                                                                                                                                                                                                                                                 │
│ Expiry: 2022-03-25                                                                                                                                                                                                                                                           │
│                                                                                                                                                                                                                                                                              │
│     pick          long, short, or none (default) underlying asset                                                                                                                                                                                                            │
│                                                                                                                                                                                                                                                                              │
│ Underlying Asset: Long                                                                                                                                                                                                                                                       │
│                                                                                                                                                                                                                                                                              │
│     list          list available strike prices for calls and puts                                                                                                                                                                                                            │
│                                                                                                                                                                                                                                                                              │
│     add           add option to the list of the options to be plotted                                                                                                                                                                                                        │
│     rmv           remove option from the list of the options to be plotted                                                                                                                                                                                                   │
│                                                                                                                                                                                                                                                                              │
│     sop           selected options                                                                                                                                                                                                                                           │
│     plot          show the option payoff diagram                                                                                                                                                                                                                             │
│                                                                                                                                                                                                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Gamestonk Terminal ─╯
```
