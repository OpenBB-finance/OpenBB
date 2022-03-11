```
usage: queries [-l LIMIT] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Print top related queries with this stock's query. [Source: Google]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of top related queries to print. (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:
```
2022 Feb 16, 10:38 (✨) /stocks/ba/ $ queries
 Top AMZN's related queries
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ query            ┃ value ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ amzn stock       │ 100%  │
├──────────────────┼───────┤
│ amzn price       │ 31%   │
├──────────────────┼───────┤
│ amzn stock price │ 26%   │
├──────────────────┼───────┤
│ aapl             │ 25%   │
├──────────────────┼───────┤
│ tsla             │ 18%   │
├──────────────────┼───────┤
│ aapl stock       │ 15%   │
├──────────────────┼───────┤
│ fb stock         │ 12%   │
├──────────────────┼───────┤
│ msft             │ 12%   │
├──────────────────┼───────┤
│ tsla stock       │ 12%   │
├──────────────────┼───────┤
│ goog             │ 9%    │
└──────────────────┴───────┘
```
