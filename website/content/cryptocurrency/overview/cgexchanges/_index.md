```
usage: cgexchanges [-l N] [-s {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Exchanges You can display only N number exchanges with --limit parameter. You can sort data by Trust_Score, Id, Name, Country,
Year_Established, Trade_Volume_24h_BTC with --sort and also with --descend flag to sort descending. Flag --urls will display urls. Displays:
Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}, --sort {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
