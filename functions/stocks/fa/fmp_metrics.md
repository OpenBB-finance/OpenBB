---
title: fmp_metrics
description: OpenBB SDK Function
---

# fmp_metrics

## stocks_fa_fmp_model.get_key_metrics

```python title='openbb_terminal/decorators.py'
def get_key_metrics() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L415)

Description: Get key metrics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | None | False |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key metrics |

## Examples

