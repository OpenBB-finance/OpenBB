```
usage: softs [-s {ticker,last,change,prevClose}] [-a] [-h] [--export {csv,json,xlsx}]
```

Softs future overview. [Source: Finviz]

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
2022 Feb 15, 05:29 (✨) /economy/ $ softs
                   Future Table
┌──────────────┬───────────┬─────────┬────────────┐
│              │ prevClose │ last    │ change (%) │
├──────────────┼───────────┼─────────┼────────────┤
│ Sugar        │ 18.12     │ 17.58   │ -2.98      │
├──────────────┼───────────┼─────────┼────────────┤
│ Lumber       │ 1216.00   │ 1246.00 │ 2.47       │
├──────────────┼───────────┼─────────┼────────────┤
│ Coffee       │ 247.90    │ 249.60  │ 0.69       │
├──────────────┼───────────┼─────────┼────────────┤
│ Orange Juice │ 136.55    │ 135.40  │ -0.84      │
├──────────────┼───────────┼─────────┼────────────┤
│ Cotton       │ 120.61    │ 120.85  │ 0.20       │
├──────────────┼───────────┼─────────┼────────────┤
│ Cocoa        │ 2731.00   │ 2739.00 │ 0.29       │
└──────────────┴───────────┴─────────┴────────────┘
```
