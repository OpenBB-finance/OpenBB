```
usage: slopes [-d DAYS] [-a] [-t THRESHOLD] [-h] [--export {csv,json,xlsx}] [-l LIMIT]
```

Show countries with highest slopes in cases.

```
optional arguments:
  -d DAYS, --days DAYS  Number of days back to look (default: 30)
  -a, --ascend          Show in ascending order (default: False)
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold for total cases over period (default: 10000)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

```    
2022 Feb 14, 10:26 (✨) /alternative/covid/ $ slopes
Highest Sloping Cases (Cases/Day)
┌────────────────┬───────────┐
│ Country        │ Slope     │
├────────────────┼───────────┤
│ US             │ 331073.67 │
├────────────────┼───────────┤
│ France         │ 278690.89 │
├────────────────┼───────────┤
│ India          │ 197265.42 │
├────────────────┼───────────┤
│ Brazil         │ 166945.38 │
├────────────────┼───────────┤
│ Germany        │ 145740.36 │
├────────────────┼───────────┤
│ United Kingdom │ 121007.75 │
├────────────────┼───────────┤
│ Russia         │ 90106.71  │
├────────────────┼───────────┤
│ Spain          │ 87634.01  │
├────────────────┼───────────┤
│ Turkey         │ 82293.04  │
├────────────────┼───────────┤
│ Japan          │ 74577.78  │
└────────────────┴───────────┘
```
