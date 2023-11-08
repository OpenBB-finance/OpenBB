---
title: top_coins
description: This OpenBBTerminal page provides insights on how to get top crypto coins
  from sources like CoinGecko and CoinMarketCap using the 'openbb.crypto.disc.top_coins'
  function. Parameters, return types, and usage examples are clearly illustrated.
keywords:
- top cryptp coins
- CoinGecko
- openbb.crypto.disc.top_coins
- parameters
- returns
- examples
- CoinMarketCap
- limit parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.top_coins - Reference | OpenBB SDK Docs" />

Get top cryptp coins.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/sdk_helpers.py#L11)]

```python
openbb.crypto.disc.top_coins(source: str = "CoinGecko", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| source | str | Source of data, by default "CoinGecko" | CoinGecko | True |
| limit | int | Number of coins to return, by default 10 | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with top coins |
---

## Examples

```python
from openbb_terminal.sdk import openbb
top_coins = openbb.crypto.disc.top_coins()
```

```
To get 30 results from coinmarketcap, use the source parameter and the limit parameter:
```
```python
top_coins = openbb.crypto.disc.top_coins(source="CoinMarketCap", limit=30)
```

---
