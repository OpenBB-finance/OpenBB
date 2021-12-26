```
usage: cgdefi [-l N] [-s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap,Url}] [--descend] [-l]
            [--export {csv,json,xlsx}] [-h]
```

Shows Top DeFi Coins by Market Capitalization DeFi or Decentralized Finance refers to financial services that are built on top of distributed
networks with no central intermediaries. You can display only top N number of coins with --top parameter. You can sort data by Rank, Name, Symbol,
Price, Change_1h, Change_24h, Change_7d, Volume 24h, Market Cap, Url with --sort and also with --descend flag to sort descending. Flag --urls will
display urls

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap,Url}, --sort {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap,Url}
                        Sort by given column. Default: rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
