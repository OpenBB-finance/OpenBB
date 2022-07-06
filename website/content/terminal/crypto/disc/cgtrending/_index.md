```
usage: cgtrending [-h] [--export {csv,json,xlsx}]
```

Discover trending coins. Use --limit parameter to display only top N number of records.

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:45 (✨) /crypto/disc/ $ cgtrending
                 Trending coins on CoinGecko
┌────────────────────┬────────────────────┬─────────────────┐
│ Symbol             │ Name               │ Market Cap Rank │
├────────────────────┼────────────────────┼─────────────────┤
│ cellframe          │ Cellframe          │ 751             │
├────────────────────┼────────────────────┼─────────────────┤
│ dehub              │ DeHub              │ 858             │
├────────────────────┼────────────────────┼─────────────────┤
│ richquack          │ Rich Quack         │ 476             │
├────────────────────┼────────────────────┼─────────────────┤
│ smooth-love-potion │ Smooth Love Potion │ 101             │
├────────────────────┼────────────────────┼─────────────────┤
│ gala               │ Gala               │ 56              │
├────────────────────┼────────────────────┼─────────────────┤
│ looksrare          │ LooksRare          │ 157             │
├────────────────────┼────────────────────┼─────────────────┤
│ doge-dash          │ Doge Dash          │ 950             │
└────────────────────┴────────────────────┴─────────────────┘
 ```
