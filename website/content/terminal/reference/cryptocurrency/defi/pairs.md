---
title: pairs
description: OpenBB Terminal Function
---

# pairs

Displays Lastly added pairs on Uniswap DEX. [Source: https://thegraph.com/en/]

### Usage

```python
usage: pairs [-l LIMIT] [-v VOL] [-tx TX] [--days DAY] [-s {created,pair,token0,token1,volumeUSD,txCount,totalSupply}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of records to display | 10 | True | None |
| vol | Minimum trading volume | 100 | True | range(1, 1000) |
| tx | Minimum number of transactions | 100 | True | range(1, 1000) |
| days | Number of days the pair has been active, | 10 | True | range(1, 1000) |
| sortby | Sort by given column. Default: created | created | True | created, pair, token0, token1, volumeUSD, txCount, totalSupply |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

