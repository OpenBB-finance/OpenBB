```
usage: meats [-s {ticker,last,change,prevClose}] [-a] [-h] [--export {csv,json,xlsx}]
```

Meats future overview. [Source: Finviz]

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
2022 Feb 15, 05:24 (✨) /economy/ $ meats
                   Future Table
┌───────────────┬───────────┬────────┬────────────┐
│               │ prevClose │ last   │ change (%) │
├───────────────┼───────────┼────────┼────────────┤
│ Lean Hogs     │ 102.22    │ 102.22 │ 0.00       │
├───────────────┼───────────┼────────┼────────────┤
│ Live Cattle   │ 146.18    │ 146.38 │ 0.14       │
├───────────────┼───────────┼────────┼────────────┤
│ Feeder Cattle │ 166.22    │ 166.97 │ 0.45       │
└───────────────┴───────────┴────────┴────────────┘
```
