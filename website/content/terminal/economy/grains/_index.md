```
usage: grains [-s {ticker,last,change,prevClose}] [-a] [-h] [--export {csv,json,xlsx}]
```

Grains future overview. [Source: Finviz]

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
2022 Feb 15, 04:59 (✨) /economy/ $ grains
                   Future Table
┌──────────────┬───────────┬─────────┬────────────┐
│              │ prevClose │ last    │ change (%) │
├──────────────┼───────────┼─────────┼────────────┤
│ Wheat        │ 799.25    │ 782.50  │ -2.10      │
├──────────────┼───────────┼─────────┼────────────┤
│ Soybeans     │ 1570.00   │ 1560.75 │ -0.59      │
├──────────────┼───────────┼─────────┼────────────┤
│ Rough Rice   │ 15.05     │ 14.99   │ -0.40      │
├──────────────┼───────────┼─────────┼────────────┤
│ Oats         │ 745.50    │ 737.25  │ -1.11      │
├──────────────┼───────────┼─────────┼────────────┤
│ Soybean Meal │ 448.40    │ 446.80  │ -0.36      │
├──────────────┼───────────┼─────────┼────────────┤
│ Soybean oil  │ 65.81     │ 65.24   │ -0.87      │
├──────────────┼───────────┼─────────┼────────────┤
│ Corn         │ 655.75    │ 647.50  │ -1.26      │
├──────────────┼───────────┼─────────┼────────────┤
│ Canola       │ 1009.50   │ 1009.20 │ -0.03      │
└──────────────┴───────────┴─────────┴────────────┘
```
