---
title: load_bl_views
description: This page documents the 'load_bl_views' function, part of the OpenBB's
  portfolio optimization toolset which allows users to load an Excel file with views
  for the Black Litterman model. Learn about inputs, outputs and usage.
keywords:
- load_bl_views
- OpenBB portfolio optimization
- Black Litterman model
- Excel file loading
- p_views matrix
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.po.load_bl_views - Reference | OpenBB SDK Docs" />

Load a Excel file with views for Black Litterman model.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/excel_model.py#L101)]

```python
openbb.portfolio.po.load_bl_views(excel_file: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| excel_file | str | The location of the Excel file that needs to be loaded. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | Returns a list with p_views matrix |
---
