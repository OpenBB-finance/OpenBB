---
title: screen
description: OpenBB SDK Function
---

# screen

## etf_scr_model.etf_screener

```python title='openbb_terminal/etf/screener/screener_model.py'
def etf_screener(preset: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/screener/screener_model.py#L43)

Description: Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Screener to use from presets | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Screened dataframe |

## Examples

