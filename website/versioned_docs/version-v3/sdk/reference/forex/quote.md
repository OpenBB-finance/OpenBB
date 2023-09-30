---
title: quote
description: OpenBB SDK Function
---

# quote

Get forex quote.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/sdk_helpers.py#L9)]

```python
openbb.forex.quote(symbol: str, source: str = "YahooFinance")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Forex symbol to get quote for. | None | False |
| source | str | Source to get quote from, by default "YahooFinance" | YahooFinance | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of quote data. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
EUR_USD_quote = openbb.forex.quote("EURUSD")
```

```
This also supports AlphaVantage and will handle different conventions
```
```python
EUR_USD= openbb.forex.quote("EUR/USD", source="AlphaVantage")
```

---

