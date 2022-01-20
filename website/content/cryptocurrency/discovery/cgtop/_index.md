```
usage: cgtop [-c CATEGORY] [-l N] [-s {Symbol,Name,Price [$],Market Cap [$],Market Cap Rank,Volume [$]}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows Largest Gainers - coins which gain the most in given period. You can use parameter --period to set which timeframe are you interested in: 1h,
{14d,1h,1y,200d,24h,30d,7d} You can look on only top N number of records with --limit, You can sort by {Symbol,Name,Price [$],Market Cap [$],Market Cap Rank,Volume [$]} with --sort

```
optional arguments:
  -c CATEGORY, --category CATEGORY
                        Category to check top coins. Empty for none.
  -l N, --limit N       display N records (default: 15)
  -s {Symbol,Name,Price [$],Market Cap [$],Market Cap Rank,Volume [$]}, --sort {Symbol,Name,Price [$],Market Cap [$],Market Cap Rank,Volume [$]}
                        Sort by given column (default: Market Cap Rank)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
