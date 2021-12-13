```
usage: cgsentiment [-l N] [-s {Rank,Name,Price_BTC,Price_USD}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Discover coins with positive sentiment. Use --top parameter to display only top N number of records, You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag to sort descending. Flag --urls will display one additional column with all coingecko urls for listed coins. sentiment will display: Rank, Name, Price_BTC, Price_USD

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Rank,Name,Price_BTC,Price_USD}, --sort {Rank,Name,Price_BTC,Price_USD}
                        Sort by given column. Default: rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls. If you will use that flag you will additional column with urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
