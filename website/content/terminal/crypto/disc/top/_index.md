```
usage: cgtop top [-c CATEGORY] [-l LIMIT] [-s {Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} [{Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} ...]] [--reverse] [-h] [--export EXPORT] [--source {CoinGecko,CoinMarketCap}]
```

Display N coins from the data source, if the data source is CoinGecko it can receive a category as argument (-c
decentralized-finance-defi or -c stablecoins) and will show only the top coins in that category. can also receive sort
arguments (these depend on the source), e.g., --sort Volume [$] You can sort by {Symbol,Name,Price [$],Market
Cap,Market Cap Rank,Volume [$]} with CoinGecko Number of coins to show: -l 10

```
  -c CATEGORY, --category CATEGORY
                        Category (e.g., stablecoins). Empty for no category. Only works for 'CoinGecko' source.
                        (default: )
  -l LIMIT, --limit LIMIT
                        Limit of records (default: 10)
  -s {Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} [{Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} ...], --sort {Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} [{Symbol,Name,Volume [$],Market Cap,Market Cap Rank,7D Change [%],24H Change [%]} ...]
                        Sort by given column. Default: Market Cap Rank (default: Market Cap Rank)
-r, --reverse           Data is sorted in descending order by default. Reverse
                        flag will sort it in an ascending way. Only works when raw
                        data is displayed. (default: False)
-h, --help              show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {CoinGecko,CoinMarketCap}
                        Data source to select from (default: CoinGecko)
```

Example:
```
2022 Feb 15, 06:44 (✨) /crypto/disc/ $ top
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
