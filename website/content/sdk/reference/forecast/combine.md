---
title: combine
description: Learn how to use the combine function in OpenBB programming library to
  add columns to dataframes. This page provides details on parameters, returns, and
  even source code.
keywords:
- Combine function
- Data manipulation
- Dataframes
- Forecasting model
- Python library
- Programming
- Source code
- Add column
- Data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.combine - Reference | OpenBB SDK Docs" />

Adds the given column of df2 to df1

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L409)]

```python
openbb.forecast.combine(df1: pd.DataFrame, df2: pd.DataFrame, column: str, dataset: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| df1 | pd.DataFrame | The dataframe to add a column to | None | False |
| df2 | pd.DataFrame | The dataframe to lose a column | None | False |
| column | str | The column to transfer | None | False |
| dataset | str | A name for df2 (shows in name of new column) |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The new dataframe |
---
