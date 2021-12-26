```
usage: cgdex [-l N] [-s {Name,Rank,Volume_24h,Coins,Pairs,Visits,Most_Traded,Market_Share}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Decentralized Exchanges on CoinGecko by Trading Volume You can display only top N number of coins with --top parameter. You can sort data
by Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share by volume with --sort and also with --descend flag to sort descending.
Display columns: Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Name,Rank,Volume_24h,Coins,Pairs,Visits,Most_Traded,Market_Share}, --sort {Name,Rank,Volume_24h,Coins,Pairs,Visits,Most_Traded,Market_Share}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
