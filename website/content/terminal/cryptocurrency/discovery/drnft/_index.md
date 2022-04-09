```
usage: drnft [-l N] [-s {Name,Protocols,Floor Price [$],Avg Price [$],Market Cap [$],Volume [$]}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows top NFT collections [Source: https://dappradar.com/]

Accepts --sort {Name,Protocols,Floor Price [$],Avg Price [$],Market Cap [$],Volume [$]} to sort by column

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s --sort {Name,Protocols,Floor Price [$],Avg Price [$],Market Cap [$],Volume [$]}
                        Sort by given column
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
