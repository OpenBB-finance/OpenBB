```
usage: cgderivatives [-t TOP] [-s {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto derivatives from CoinGecko Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin. The most popular crypto derivatives are crypto futures,
crypto options, and perpetual contracts. You can look on only top N number of records with --top, You can sort by Rank, Market, Symbol, Price,
Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h with --sort and also with --descend flag to set it to sort descending.
Displays: Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 15)
  -s {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}, --sort {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
