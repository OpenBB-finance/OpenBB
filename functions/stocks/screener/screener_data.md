---
title: screener_data
description: OpenBB SDK Function
---

# screener_data

## stocks_screener_finviz_model.get_screener_data

```python title='openbb_terminal/stocks/screener/finviz_model.py'
def get_screener_data(preset_loaded: str, data_type: str, limit: int, ascend: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/finviz_model.py#L76)

Description: Screener Overview

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Loaded preset filter | None | False |
| data_type | str | Data type between: overview, valuation, financial, ownership, performance, technical | None | False |
| limit | int | Limit of stocks filtered with presets to print | None | False |
| ascend | bool | Ascended order of stocks filtered to print | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with loaded filtered stocks |

## Examples

