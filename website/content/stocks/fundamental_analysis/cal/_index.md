```
usage: cal [-h] [--export {csv,json,xlsx}]
```

Calendar earnings of the company. Including revenue and earnings estimates. [Source: Yahoo Finance]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example shown for the loaded ticker MSFT:
```
2022 Feb 16, 04:47 (✨) /stocks/fa/ $ cal
                                             Ticker Calendar Earnings
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Earnings Date ┃ Earnings Average ┃ Earnings Low ┃ Earnings High ┃ Revenue Average ┃ Revenue Low ┃ Revenue High ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 04/25/2022    │ 2.190            │ 2.140        │ 2.290         │ 49.055 B        │ 48.652 B    │ 49.719 B     │
├───────────────┼──────────────────┼──────────────┼───────────────┼─────────────────┼─────────────┼──────────────┤
│ 04/29/2022    │ 2.190            │ 2.140        │ 2.290         │ 49.055 B        │ 48.652 B    │ 49.719 B     │
└───────────────┴──────────────────┴──────────────┴───────────────┴─────────────────┴─────────────┴──────────────┘
```
