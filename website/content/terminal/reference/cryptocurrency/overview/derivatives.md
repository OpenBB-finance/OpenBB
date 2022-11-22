---
title: derivatives
description: OpenBB Terminal Function
---

# derivatives

Shows list of crypto derivatives from CoinGecko Crypto derivatives are secondary contracts or financial tools that derive their value from a primary underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin. The most popular crypto derivatives are crypto futures, crypto options, and perpetual contracts. You can look on only N number of records with --limit, You can sort by Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h with by and also with --reverse flag to set it to sort descending. Displays: Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h

### Usage

```python
usage: derivatives [-l LIMIT] [-s {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: Rank | Rank | True | Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h |
| reverse | Data is sorted in ascending order by default. Reverse flag will sort it in an descending way. Only works when raw data is displayed. | False | True | None |
---

