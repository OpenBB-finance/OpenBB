---
title: top_coins
description: OpenBB SDK Function
---

# top_coins

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

