```
usage: cgvolume [-l N] [-s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Coins by Trading Volume. You can display only top N number of coins with --top parameter. You can sort data by on of columns Rank, Name,
Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap with --sort parameter and also with --descend flag to sort descending.
Displays columns: Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}, --sort {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
