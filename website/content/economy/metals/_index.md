```
usage: metals [-s {ticker,last,change,prevClose}] [-a] [-h] [--export {csv,json,xlsx}]
```

Metals future overview. [Source: Finviz]

```
optional arguments:
  -s {ticker,last,change,prevClose}, --sortby {ticker,last,change,prevClose}
  -a, -ascend           Flag to sort in ascending order (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 05:24 (✨) /economy/ $ metals
                  Future Table
┌───────────┬───────────┬─────────┬────────────┐
│           │ prevClose │ last    │ change (%) │
├───────────┼───────────┼─────────┼────────────┤
│ Silver    │ 23.85     │ 23.43   │ -1.77      │
├───────────┼───────────┼─────────┼────────────┤
│ Platinum  │ 1028.00   │ 1020.60 │ -0.72      │
├───────────┼───────────┼─────────┼────────────┤
│ Palladium │ 2346.00   │ 2284.00 │ -2.64      │
├───────────┼───────────┼─────────┼────────────┤
│ Copper    │ 4.51      │ 4.53    │ 0.53       │
├───────────┼───────────┼─────────┼────────────┤
│ Gold      │ 1869.40   │ 1855.30 │ -0.75      │
└───────────┴───────────┴─────────┴────────────┘
```
