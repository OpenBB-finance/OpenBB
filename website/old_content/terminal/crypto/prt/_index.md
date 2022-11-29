```
usage: prt [--vs COIN] [--price NUM] [--top NUM] [--export {csv,json,xlsx}] [-h]
```

Tool to calculate potential returns of a certain coin. It will take the loaded coin and compare with either another coin specified with argument `--vs`, with a target price specified with argument `--price`, or with the current N coins with biggest market cap with `--top`.

```
optional arguments:
  --vs COIN             Symbol of coin to compare loaded coin with (e.g., BTC)
  -p NUM --price NUM    Target price to compute potential returns (e.g., 5)
  -t NUM --top   NUM    Top NUM coins to compare with (e.g., 5)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Examples:

`load algo/prt --price 2`
`load algo/prt --vs btc`
`load algo/prt --top 5`
