---
title: comparison
description: OpenBB SDK Function
---

# comparison

Compare regression results between Panel Data regressions.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L437)]

```python
openbb.econometrics.comparison(regressions: Dict, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regressions | Dict | Dictionary with regression results. | None | False |
| export | str | Format to export data |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Returns a PanelModelComparison which shows an overview of the different regression results. |
---

