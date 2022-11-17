---
title: search
description: OpenBB SDK Function
---

# search

## stocks_helper.search

```python title='openbb_terminal/stocks/stocks_helper.py'
def search(query: str, country: str, sector: str, industry: str, exchange_country: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L98)

Description: Search selected query for tickers.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | The search term used to find company tickers | None | False |
| country | str | Search by country to find stocks matching the criteria | None | False |
| sector | str | Search by sector to find stocks matching the criteria | None | False |
| industry | str | Search by industry to find stocks matching the criteria | None | False |
| exchange_country | str | Search by exchange country to find stock matching | None | False |
| limit | int | The limit of companies shown. | None | False |
| export | str | Export data | None | False |

## Returns

This function does not return anything

## Examples

