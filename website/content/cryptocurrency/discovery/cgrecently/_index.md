```
usage: cgrecently [-t TOP] [-s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Added,Url}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows recently added coins on CoinGecko. You can display only top N number of coins with --top parameter. You can sort data by Rank, Name, Symbol,
Price, Change_1h, Change_24h, Added with --sort and also with --descend flag to sort descending. Flag --links will display urls

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Added,Url}, --sort {Rank,Name,Symbol,Price,Change_1h,Change_24h,Added,Url}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -l, --links           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
