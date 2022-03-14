```
usage: cgtop [-c CATEGORY] [-l LIMIT] [-s SORTBY [SORTBY ...]] [-h] [--export {csv,json,xlsx}]
```

Shows Largest Gainers - coins which gain the most in given period. You can use parameter --period to set which timeframe are you interested in: 1h,
{14d,1h,1y,200d,24h,30d,7d} You can look on only top N number of records with --limit, You can sort by {Symbol,Name,Price [$],Market Cap [$],Market Cap Rank,Volume [$]} with --sort

```
optional arguments:
  -c CATEGORY, --category CATEGORY
                        Category (e.g., stablecoins). Empty for no category (default: )
  -l LIMIT, --limit LIMIT
                        Limit of records (default: 10)
  -s SORTBY [SORTBY ...], --sort SORTBY [SORTBY ...]
                        Sort by given column. Default: Market Cap Rank (default: Market Cap Rank)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:44 (✨) /crypto/disc/ $ cgtop
┌────────┬──────────────┬────────────┬────────────────┬─────────────────┬───────────────┬────────────────┐
│ Symbol │ Name         │ Volume [$] │ Market Cap [$] │ Market Cap Rank │ 7D Change [%] │ 24H Change [%] │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ btc    │ Bitcoin      │ 20.6B      │ 838.8B         │ 1               │ 0.93          │ 4.77           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ eth    │ Ethereum     │ 14.4B      │ 370.6B         │ 2               │ -1.53         │ 7.77           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ usdt   │ Tether       │ 43.3B      │ 78.5B          │ 3               │ -0.01         │ -0.05          │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ bnb    │ Binance Coin │ 1.8B       │ 72.2B          │ 4               │ -1.01         │ 8.18           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ usdc   │ USD Coin     │ 3B         │ 52.6B          │ 5               │ 0.25          │ 0.17           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ xrp    │ XRP          │ 3.2B       │ 39.9B          │ 6               │ 0.71          │ 5.51           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ ada    │ Cardano      │ 1B         │ 34.9B          │ 7               │ -9.04         │ 5.52           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ sol    │ Solana       │ 1.8B       │ 32.7B          │ 8               │ -12.54        │ 10.07          │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ luna   │ Terra        │ 1B         │ 22.4B          │ 9               │ -5.26         │ 8.67           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ AVAX   │ Avalanche    │ 899.9M     │ 21.7B          │ 10              │ 6.28          │ 12.72          │
└────────┴──────────────┴────────────┴────────────────┴─────────────────┴───────────────┴────────────────┘
```
