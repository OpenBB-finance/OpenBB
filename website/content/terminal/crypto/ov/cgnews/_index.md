```
usage: cgnews [-l N] [-s {Index,Title,Author,Posted}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows latest crypto news from CoinGecko. You will see Index, Title, Author, Posted columns. You can sort by each of column above, using --sort
parameter and also do it descending with --descend flagTo display urls to news use --urls flag.

```
optional arguments:
  -l N, --limit N      N number of news >=10 (default: 15)
  -s {Index,Title,Author,Posted}, --sort {Index,Title,Author,Posted}
                        Sort by given column. Default: index (default: Index)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls. If you will use that flag you will additional column with urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
