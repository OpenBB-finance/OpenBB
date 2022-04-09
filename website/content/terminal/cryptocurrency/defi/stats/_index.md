```
usage: stats [-h] [--export {csv,json,xlsx}]
```
Display base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:33 (✨) /crypto/defi/ $ stats
 Uniswap DEX Base Statistics
┌───────────────────┬────────┐
│ Metric            │ Value  │
├───────────────────┼────────┤
│ totalVolumeUSD    │ 393.2B │
├───────────────────┼────────┤
│ totalLiquidityUSD │ 3.3B   │
├───────────────────┼────────┤
│ pairCount         │ 63.3K  │
├───────────────────┼────────┤
│ txCount           │ 73.6M  │
├───────────────────┼────────┤
│ totalLiquidityETH │ 1.1M   │
└───────────────────┴────────┘
```
