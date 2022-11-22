---
title: indexes
description: OpenBB Terminal Function
---

# indexes

Shows list of crypto indexes from CoinGecko. Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market cap. You can display only N number of indexes with --limit parameter. You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sortby and also with --reverse flag to sort descending. Displays: Rank, Name, Id, Market, Last, MultiAsset

### Usage

```python
usage: indexes [-l LIMIT] [-s {Rank,Name,Id,Market,Last,MultiAsset}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: Rank | Rank | True | Rank, Name, Id, Market, Last, MultiAsset |
| reverse | Data is sorted in ascending order by default. Reverse flag will sort it in an descending way. Only works when raw data is displayed. | False | True | None |
---

