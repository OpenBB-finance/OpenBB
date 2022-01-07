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
2022 Jan 05, 17:01 (✨) /alternative/covid/ $ slopes -l 4

Highest Sloping Cases     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Country        ┃ Slope     ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ US             │ 210153.96 │
├────────────────┼───────────┤
│ United Kingdom │ 104611.68 │
├────────────────┼───────────┤
│ France         │ 81275.88  │
├────────────────┼───────────┤
│ Spain          │ 47986.82  │
└────────────────┴───────────┘

```