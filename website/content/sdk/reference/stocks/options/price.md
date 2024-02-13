---
title: price
description: Get Option current price for a stock
keywords:
- stocks
- options
- price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.price - Reference | OpenBB SDK Docs" />

Get Option current price for a stock.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_sdk_helper.py#L86)]

```python wordwrap
openbb.stocks.options.price(symbol: str, source: str = "Nasdaq")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get chain for | None | False |
| source | str | Source to get data, by default "Nasdaq". Can be Nasdaq, Tradier, or YahooFinance | Nasdaq | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | float of current price |
---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
```

---

