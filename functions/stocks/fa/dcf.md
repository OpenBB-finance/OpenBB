---
title: dcf
description: OpenBB SDK Function
---

# dcf

## stocks_fa_fmp_model.get_dcf

```python title='openbb_terminal/decorators.py'
def get_dcf() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L173)

Description: Get stocks dcf from FMP

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | None | False |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of dcf data |

## Examples

