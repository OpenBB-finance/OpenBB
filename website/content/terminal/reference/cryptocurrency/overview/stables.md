---
title: stables
description: OpenBB Terminal Function
---

# stables

Shows stablecoins by market capitalization. Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference like the U.S. dollar or to a commodity's price such as gold. You can display only N number of coins with --limit parameter. You can sort data by {} with --sortby

### Usage

```python
usage: stables [-l LIMIT] [-s {Symbol,Name,Price_[$],Market_Cap_[$],Market_Cap_Rank,Change_7d_[%],Change_24h_[%],Volume_[$]}] [-r] [--pie]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: market_cap | Market_Cap_[$] | True | Symbol, Name, Price_[$], Market_Cap_[$], Market_Cap_Rank, Change_7d_[%], Change_24h_[%], Volume_[$] |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| pie | Flag to show pie chart | False | True | None |
---

