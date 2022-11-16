---
title: fmp_ratios
description: OpenBB SDK Function
---

# fmp_ratios

## stocks_fa_fmp_model.get_key_ratios

```python title='openbb_terminal/decorators.py'
def get_key_ratios() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L457)

Description: Get key ratios

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | None | False |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key ratios |

## Examples

