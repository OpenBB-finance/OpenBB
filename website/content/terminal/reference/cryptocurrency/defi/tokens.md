---
title: tokens
description: OpenBB Terminal Function
---

# tokens

Display tokens trade-able on Uniswap DEX [Source: https://thegraph.com/en/]

### Usage

```python
usage: tokens [--skip SKIP] [--limit LIMIT] [-s {index,symbol,name,tradeVolumeUSD,totalLiquidity,txCount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| skip | Number of records to skip | 0 | True | range(1, 1000) |
| limit | Number of records to display | 20 | True | None |
| sortby | Sort by given column. Default: index | index | True | index, symbol, name, tradeVolumeUSD, totalLiquidity, txCount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

