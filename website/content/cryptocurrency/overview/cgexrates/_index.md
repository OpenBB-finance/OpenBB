```
usage: cgexrates [-t TOP] [-s {Index,Name,Unit,Value,Type}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto, fiats, commodity exchange rates from CoinGecko You can look on only top N number of records with --top, You can sort by Index,
Name, Unit, Value, Type, and also use --descend flag to sort descending.

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Index,Name,Unit,Value,Type}, --sort {Index,Name,Unit,Value,Type}
                        Sort by given column. Default: Index (default: Index)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
