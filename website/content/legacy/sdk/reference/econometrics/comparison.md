---
title: comparison
description: This page provides a comparison function for Panel Data regression results
  in the openbb terminal. It allows exporting the comparison data and returns an overview
  of the different regression results as a PanelModelComparison.
keywords:
- Panel Data regression
- regression results comparison
- econometrics
- openbb terminal
- export data
- PanelModelComparison
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.comparison - Reference | OpenBB SDK Docs" />

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
