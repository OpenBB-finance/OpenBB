```
usage: arktrades [-n NUM] [-h] [--export {csv,json,xlsx}]
```

Get trades for ticker across all ARK funds.

```
optional arguments:
  -n NUM, --num NUM     Number of rows to show
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

Output:

```python
(✨) (stocks)>(dd)> arktrades
╒════════════╤══════════╤══════════╤════════╤═════════════╕
│ date       │   shares │   weight │ fund   │ direction   │
╞════════════╪══════════╪══════════╪════════╪═════════════╡
│ 2021-05-20 │      188 │   0.0007 │ ARKF   │ Sell        │
├────────────┼──────────┼──────────┼────────┼─────────────┤
│ 2021-05-18 │     2500 │   0.0091 │ ARKF   │ Sell        │
├────────────┼──────────┼──────────┼────────┼─────────────┤
│ 2021-05-17 │   188455 │   0.6945 │ ARKF   │ Sell        │
├────────────┼──────────┼──────────┼────────┼─────────────┤
│ 2021-05-10 │    87560 │   0.3057 │ ARKF   │ Sell        │
├────────────┼──────────┼──────────┼────────┼─────────────┤
│ 2021-05-06 │   298505 │   1.0040 │ ARKF   │ Sell        │
├────────────┼──────────┼──────────┼────────┼─────────────┤
```
