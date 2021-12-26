```
usage: cgnft [-l N] [-s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows Top NFT Coins by Market Capitalization NFT (Non-fungible Token) refers to digital assets with unique characteristics. Examples of NFT include
crypto artwork, collectibles, game items, financial products, and more. You can display only top N number of coins with --top parameter. You can sort
data by Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap with --sort and also with --descend flag to sort descending. Flag
--urls will display urls Displays : Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap, Url

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}, --sort {Rank,Name,Symbol,Price,Change_1h,Change_24h,Change_7d,Volume_24h,Market_Cap}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
