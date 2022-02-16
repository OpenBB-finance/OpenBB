```
usage: fipo [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

See future IPOs dates. [Source: https://finnhub.io]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of future days to look for IPOs. (default: 5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 03:59 (✨) /stocks/disc/ $ fipo
                                                       Future IPO Dates
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Future     ┃ Exchange       ┃ Name                 ┃ Number of Shares ┃ Price      ┃ Status   ┃ symbol ┃ Total Shares Value ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 2022-02-16 │ NASDAQ Capital │ SMART FOR LIFE, INC. │ 1800000          │ 9.00-11.00 │ expected │ SMFL   │ 22770000           │
└────────────┴────────────────┴──────────────────────┴──────────────────┴────────────┴──────────┴────────┴────────────────────┘
```
