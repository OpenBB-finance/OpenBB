```
usage: cgyfarms [-l N] [-s {Rank,Name,Value_Locked,Return_Year}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Yield Farming Pools by Value Locked. Yield farming, also referred to as liquidity mining, is a way to generate rewards with cryptocurrency
holdings. In simple terms, it means locking up cryptocurrencies and getting rewards. You can display only top N number of coins with --top parameter.
You can sort data by Rank, Name, Value_Locked, Return_Year with --sort parameter and also with --descend flag to sort descending.

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s {Rank,Name,Value_Locked,Return_Year}, --sort {Rank,Name,Value_Locked,Return_Year}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
