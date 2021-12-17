```
usage: cgproducts [-l N] [-s {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto. You can display only N number of platforms with
--limit parameter. You can sort data by Rank, Platform, Identifier, Supply_Rate, Borrow_Rate with --sort and also with --descend flag to sort
descending. Displays: Rank, Platform, Identifier, Supply_Rate, Borrow_Rate

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}, --sort {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
