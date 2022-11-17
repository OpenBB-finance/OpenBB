---
title: av_balance
description: OpenBB SDK Function
---

# av_balance

## stocks_fa_av_model.get_balance_sheet

```python title='openbb_terminal/stocks/fundamental_analysis/av_model.py'
def get_balance_sheet(symbol: str, limit: int, quarterly: bool, ratios: bool, plot: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L253)

Description: Get balance sheets for company

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
| pd.DataFrame | DataFrame of the balance sheet |

## Examples

