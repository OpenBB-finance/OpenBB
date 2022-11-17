---
title: av_income
description: OpenBB SDK Function
---

# av_income

## stocks_fa_av_model.get_income_statements

```python title='openbb_terminal/stocks/fundamental_analysis/av_model.py'
def get_income_statements(symbol: str, limit: int, quarterly: bool, ratios: bool, plot: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L162)

Description: Get income statements for company

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of past to get | None | False |
| quarterly | bool | Flag to get quarterly instead of annual, by default False | False | True |
| ratios | bool | Shows percentage change, by default False | False | False |
| plot | bool | If the data shall be formatted ready to plot | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of income statements |

## Examples

