```
usage: ex [-l N] [-s {id,name,adjusted_volume_24h_share,fiats}] [--reverse] [--export {csv,json,xlsx}] [-h]
```

Get all exchanges found for given coin. You can display only N number of exchanges with --limit parameter. You can sort data by id, name,
adjusted_volume_24h_share, fiats --sort parameter and also with --reverse flag to sort ascending. Displays: id, name, adjusted_volume_24h_share, fiats

```
optional arguments:
  -l N, --limit N     Limit of records (default: 10)
  -s {id,name,adjusted_volume_24h_share,fiats}, --sort {id,name,adjusted_volume_24h_share,fiats}
                        Sort by given column. Default: date (default: adjusted_volume_24h_share)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
