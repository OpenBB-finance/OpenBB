```
usage: tipt [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Print top insider purchases of the day. [Source: OpenInsider]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of datarows to display (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 08:18 (✨) /stocks/ins/ $ tipt
                                                                          Insider Data
┏━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ X ┃ Filing Date ┃ Trade Date ┃ Ticker ┃ Company Name     ┃ Insider Name         ┃ Title    ┃ Trade Type   ┃ Price ┃ Qty     ┃ Owned   ┃ Diff Own ┃ Value     ┃
┡━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ M │ 2022-02-16  │ 2022-02-09 │ ZIVO   │ Zivo Bioscience, │ Maggiore Christopher │ Dir, 10% │ P - Purchase │ $3.72 │ +91,334 │ 803,105 │ +13%     │ +$340,098 │
│   │ 06:02:09    │            │        │ Inc.             │ D.                   │          │              │       │         │         │          │           │
└───┴─────────────┴────────────┴────────┴──────────────────┴──────────────────────┴──────────┴──────────────┴───────┴─────────┴─────────┴──────────┴───────────┘
M: Multiple transactions in filing; earliest reported transaction date & weighted average transaction price
```
