```
usage: dpi [-t TOP] [-s {Rank,Name,Chain,Category,TVL,Change_1D}] [--descend]
           [--export {csv,json,xlsx}] [-h]
```

Displays DeFi Pulse crypto protocols. [Source: https://defipulse.com/]

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Name,Chain,Category,TVL,Change_1D}, --sort {Rank,Name,Chain,Category,TVL,Change_1D}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
