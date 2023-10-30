---
title: last_price
description: The page provides documentation for the 'last_price' API call in the
  OpenBBTerminal project of OpenBB.finance. It details how to request for the last
  price of a specific stock option using the ticker symbol.
keywords:
- last_price
- api request
- OpenBB.finance
- stocks
- options
- tradier_model.py
- ticker symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.last_price - Reference | OpenBB SDK Docs" />

Makes api request for last price

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/tradier_model.py#L275)]

```python
openbb.stocks.options.last_price(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
|  | Last price |
---
