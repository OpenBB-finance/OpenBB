```
usage: drdex [-l N] [-s {Name,Daily Users,Daily Volume [$]}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows top decentralized exchanges [Source: https://dappradar.com/]

Accepts --sort {Name,Daily Users,Daily Volume [$]} to sort by column

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s --sort {Name,Daily Users,Daily Volume [$]}
                        Sort by given column
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
