```
usage: cggainers [-p {1h,24h,7d,14d,30d,60d,1y}] [-t TOP] [-s {Rank,Symbol,Name,Volume,Price,Change}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows Largest Gainers - coins which gain the most in given period. You can use parameter --period to set which timeframe are you interested in: 1h,
24h, 7d, 14d, 30d, 60d, 1y You can look on only top N number of records with --top, You can sort by Rank, Symbol, Name, Volume, Price, Change with
--sort and also with --descend flag to set it to sort descending. There is --links flag, which will display one additional column you all urls for
coins.

```
optional arguments:
  -p {1h,24h,7d,14d,30d,60d,1y}, --period {1h,24h,7d,14d,30d,60d,1y}
                        time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y] (default: 1h)
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Symbol,Name,Volume,Price,Change}, --sort {Rank,Symbol,Name,Volume,Price,Change}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -l, --links           Flag to show urls. If you will use that flag you will additional column with urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
