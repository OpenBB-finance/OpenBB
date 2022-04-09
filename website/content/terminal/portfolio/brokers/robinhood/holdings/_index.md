```
usage: holdings [--export {csv,json,xlsx}] [-h]
```
Display info about your trading accounts on Robinhood
```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
  ```
Sample Output:
```
╒════╤══════════╤═══════════════╤════════════╤═════════════╕
│    │ Symbol   │   MarketValue │   Quantity │   CostBasis │
╞════╪══════════╪═══════════════╪════════════╪═════════════╡
│  0 │ AMC      │         78.88 │     2      │      97.22  │
╘════╧══════════╧═══════════════╧════════════╧═════════════╛
```
