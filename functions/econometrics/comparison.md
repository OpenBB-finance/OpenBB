---
title: comparison
description: OpenBB SDK Function
---

# comparison

## econometrics_regression_model.get_comparison

```python title='openbb_terminal/econometrics/regression_model.py'
def get_comparison(regressions: Any, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L426)

Description: Compare regression results between Panel Data regressions.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regressions | Dict | Dictionary with regression results. | None | False |
| export | str | Format to export data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Returns a PanelModelComparison which shows an overview of the different regression results. | None |

## Examples

