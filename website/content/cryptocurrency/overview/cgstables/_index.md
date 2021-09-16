```
usage: cgstables [-t TOP] [-s {Rank,Name,Symbol,Price,Change_24h,Exchanges,Market_Cap,Change_30d}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows stablecoins by market capitalization. Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference like
the U.S. dollar or to a commodity's price such as gold. You can display only top N number of coins with --top parameter. You can sort data by Rank,
Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d with --sort and also with --descend flag to sort descending. Flag --links will
display stablecoins urls

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Name,Symbol,Price,Change_24h,Exchanges,Market_Cap,Change_30d}, --sort {Rank,Name,Symbol,Price,Change_24h,Exchanges,Market_Cap,Change_30d}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -l, --links           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
