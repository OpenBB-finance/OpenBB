```
usage: cgplatforms [-t TOP] [-s {Rank,Name,Category,Centralized}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Financial Platforms in which you can borrow or lend your crypto. e.g Celsius, Nexo, Crypto.com, Aave and others. You can display
only top N number of platforms with --top parameter. You can sort data by Rank, Name, Category, Centralized with --sort and also with --descend flag
to sort descending. Displays: Rank, Name, Category, Centralized, Url

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Name,Category,Centralized}, --sort {Rank,Name,Category,Centralized}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
