---
title: binance_available_quotes_for_each_coin
description: This page provides a detailed guide to the helper methods in OpenBB Terminal
  that, for every coin available on Binance, add all quote assets. It includes how
  to use the function and what it will return.
keywords:
- Binance
- cryptocurrency
- quote assets
- helper methods
- coin
- function
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.binance_available_quotes_for_each_coin - Reference | OpenBB SDK Docs" />

Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_model.py#L77)]

```python
openbb.crypto.dd.binance_available_quotes_for_each_coin()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | All quote assets for given coin<br/>{'ETH' : ['BTC', 'USDT' ...], 'UNI' : ['ETH', 'BTC','BUSD', ...] |
---
