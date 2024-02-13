---
title: voi
description: Plot volume and open interest
keywords:
- stocks
- options
- voi
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.voi - Reference | OpenBB SDK Docs" />

Plot volume and open interest

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_view.py#L289)]

```python wordwrap
openbb.stocks.options.voi(chain: pd.DataFrame, current_price: float, symbol: str, expiry: str, min_sp: float = -1, max_sp: float = -1, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | pd.Dataframe | Dataframe with options chain | None | False |
| current_price | float | Current price of selected symbol | None | False |
| symbol | str | Stock ticker symbol | None | False |
| expiry | str | Option expiration | None | False |
| min_sp | float | Min strike price | -1 | True |
| max_sp | float | Max strike price | -1 | True |
| export | str | Format for exporting data |  | True |
| sheet_name | str | Optionally specify the name of the sheet to export to | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
openbb.stocks.options.voi(
```

```
chain=aapl_chain_data,
        symbol="AAPL",
        current_price=aapl_price,
        expiry="2023-07-21",
    )
```
---

