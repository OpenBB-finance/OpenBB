---
title: coin_list
description: Technical documentation on how to get a list of coins available on CoinGecko
  using the OpenBBTerminal. It includes parameters and returns in form of a pd.DataFrame.
keywords:
- Coin List
- CoinGecko
- Source Code
- Cryptocurrency
- Discovery
- pycoingecko_model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.coin_list - Reference | OpenBB SDK Docs" />

Get list of coins available on CoinGecko [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L339)]

```python
openbb.crypto.disc.coin_list()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Coins available on CoinGecko<br/>Columns: id, symbol, name |
---
