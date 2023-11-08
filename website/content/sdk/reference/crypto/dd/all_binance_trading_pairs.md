---
title: all_binance_trading_pairs
description: This page provides the function to get all available trading pairs on
  Binance in DataFrame format with columns including symbol, baseAsset, and quoteAsset.
  This function does not require any parameters.
keywords:
- Binance
- Trading pairs
- baseAsset
- quoteAsset
- Crypto Trading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.all_binance_trading_pairs - Reference | OpenBB SDK Docs" />

Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_model.py#L58)]

```python
openbb.crypto.dd.all_binance_trading_pairs()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All available pairs on Binance<br/>Columns: symbol, baseAsset, quoteAsset |
---
