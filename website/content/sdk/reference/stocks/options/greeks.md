---
title: greeks
description: Gets the greeks for a given option
keywords:
- stocks
- options
- greeks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.greeks - Reference | OpenBB SDK Docs" />

Gets the greeks for a given option

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_sdk_helper.py#L223)]

```python wordwrap
openbb.stocks.options.greeks(current_price: float, chain: pd.DataFrame, expire: str, div_cont: float = 0, rf: Optional[float] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| current_price | float | The current price of the underlying | None | False |
| chain | pd.DataFrame | The dataframe with option chains | None | False |
| div_cont | float | The dividend continuous rate | 0 | True |
| expire | str | The date of expiration | None | False |
| rf | float | The risk-free rate | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with calculated option greeks |
---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_chain = openbb.stocks.options.chains("AAPL", source="Tradier")
aapl_last_price = openbb.stocks.options.last_price("AAPL")
greeks = openbb.stocks.options.greeks(aapl_last_price, aapl_chain, aapl_chain.iloc[0, 2])
```

---

