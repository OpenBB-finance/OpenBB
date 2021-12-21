```
usage: cgcategories [-l N] [-s {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]

```

Shows top cryptocurrency categories by market capitalization. It includes categories like: stablecoins, defi, solana ecosystem, polkadot ecosystem
and many others. "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag" "To display urls use
--urls flag.", Displays: Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h, Coins,

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}, --sort {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls. If you will use that flag you will additional column with urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
