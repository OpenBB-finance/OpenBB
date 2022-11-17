---
title: fred_notes
description: OpenBB SDK Function
---

# fred_notes

## economy_fred_model.get_series_notes

```python title='openbb_terminal/decorators.py'
def get_series_notes() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L69)

Description: Get series notes. [Source: FRED]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| search_query | str | Text query to search on fred series notes database | None | False |
| limit | int | Maximum number of series notes to display | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of matched series |

## Examples

