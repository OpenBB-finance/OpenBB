```
usage: cgindexes [-l N] [-s {Rank,Name,Id,Market,Last,MultiAsset}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto indexes from CoinGecko. Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market
cap. You can display only N number of indexes with --limit parameter. You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sort and
also with --descend flag to sort descending. Displays: Rank, Name, Id, Market, Last, MultiAsset

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Name,Id,Market,Last,MultiAsset}, --sort {Rank,Name,Id,Market,Last,MultiAsset}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
