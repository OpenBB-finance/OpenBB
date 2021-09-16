```
usage: ex [-t TOP] [-s {id,name,adjusted_volume_24h_share,fiats}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Get all exchanges found for given coin. You can display only top N number of exchanges with --top parameter. You can sort data by id, name,
adjusted_volume_24h_share, fiats --sort parameter and also with --descend flag to sort descending. Displays: id, name, adjusted_volume_24h_share, fiats

```
optional arguments:
  -t TOP, --top TOP     Limit of records (default: 10)
  -s {id,name,adjusted_volume_24h_share,fiats}, --sort {id,name,adjusted_volume_24h_share,fiats}
                        Sort by given column. Default: date (default: adjusted_volume_24h_share)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
