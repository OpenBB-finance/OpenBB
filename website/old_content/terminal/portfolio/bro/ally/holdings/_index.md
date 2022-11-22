```
usage: holdings [--export {csv,json,xlsx}] [-h]
```

Display info about your trading accounts on Ally
```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
  ```
Example output:
```
╒══════╤════════════╤═════════════╤═══════════════╤════════╕
│      │   Quantity │   CostBasis │   MarketValue │    PnL │
╞══════╪════════════╪═════════════╪═══════════════╪════════╡
│ AAPL │       6.02 │      576.90 │        864.53 │ 287.63 │
├──────┼────────────┼─────────────┼───────────────┼────────┤
│ MSFT │       2.01 │      358.09 │        595.22 │ 237.13 │
╘══════╧════════════╧═════════════╧═══════════════╧════════╛
```
