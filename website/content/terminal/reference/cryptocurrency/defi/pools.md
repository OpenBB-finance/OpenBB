---
title: pools
description: OpenBB Terminal Function
---

# pools

Display uniswap pools by volume. [Source: https://thegraph.com/en/]

### Usage

```python
usage: pairs [-l LIMIT] [-s {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of records to display | 10 | True | None |
| sortby | Sort by given column. Default: volumeUSD | volumeUSD | True | volumeUSD, token0.name, token0.symbol, token1.name, token1.symbol, volumeUSD, txCount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

