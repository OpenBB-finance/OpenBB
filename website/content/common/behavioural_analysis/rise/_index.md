```
usage: rise [-l LIMIT] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Print top rising related queries with this stock's query. [Source: Google]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of top rising related queries to print. (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:
```
2022 Feb 16, 10:40 (✨) /stocks/ba/ $ rise
Top rising AAPL's related queries
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ query           ┃ value  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ nio stock       │ 227850 │
├─────────────────┼────────┤
│ nio             │ 183950 │
├─────────────────┼────────┤
│ pltr            │ 103100 │
├─────────────────┼────────┤
│ pltr stock      │ 82800  │
├─────────────────┼────────┤
│ mrna stock      │ 75050  │
├─────────────────┼────────┤
│ zm stock        │ 67850  │
├─────────────────┼────────┤
│ nio stock price │ 64000  │
├─────────────────┼────────┤
│ zm              │ 63500  │
├─────────────────┼────────┤
│ bynd            │ 61450  │
├─────────────────┼────────┤
│ bynd stock      │ 47450  │
└─────────────────┴────────┘
```
