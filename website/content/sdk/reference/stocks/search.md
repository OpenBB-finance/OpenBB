---
title: search
description: OpenBB SDK Function
---

# search

Search selected query for tickers.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L98)]

```python
openbb.stocks.search(query: str = "", country: str = "", sector: str = "", industry: str = "", exchange_country: str = "", limit: int = 0, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | The search term used to find company tickers |  | True |
| country | str | Search by country to find stocks matching the criteria |  | True |
| sector | str | Search by sector to find stocks matching the criteria |  | True |
| industry | str | Search by industry to find stocks matching the criteria |  | True |
| exchange_country | str | Search by exchange country to find stock matching |  | True |
| limit | int | The limit of companies shown. | 0 | True |
| export | str | Export data |  | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.search(country="united states", exchange_country="Germany")
```

---

