---
title: chains
description: OpenBB SDK Function
---

# chains

Get Option Chain For A Stock.  No greek data is returned

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_sdk_helper.py#L20)]

```python
openbb.stocks.options.chains(symbol: str, source: str = "Nasdaq", expiration: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get chain for | None | False |
| source | str | Source to get data from, by default "Nasdaq" | Nasdaq | True |
| expiration | Union[str, None] | Date to get chain for.  By default returns all dates | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of full option chain. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_option_chain = openbb.stocks.options.chains("AAPL", source = "Nasdaq")
```

```
To get a specific expiration date, use the expiration parameter
```
```python
aapl_chain_date = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
```

---

