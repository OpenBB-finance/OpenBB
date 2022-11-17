---
title: screener
description: OpenBB SDK Function
---

# screener

## stocks_screener_finviz_view.screener

```python title='openbb_terminal/stocks/screener/finviz_view.py'
def screener(loaded_preset: str, data_type: str, limit: int, ascend: bool, sortby: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/finviz_view.py#L127)

Description: Screener one of the following: overview, valuation, financial, ownership, performance, technical.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_preset | str | Preset loaded to filter for tickers | None | False |
| data_type | str | Data type string between: overview, valuation, financial, ownership, performance, technical | None | False |
| limit | int | Limit of stocks to display | None | False |
| ascend | bool | Order of table to ascend or descend | None | False |
| sortby | str | Column to sort table by | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List[str] | List of stocks that meet preset criteria |

## Examples

