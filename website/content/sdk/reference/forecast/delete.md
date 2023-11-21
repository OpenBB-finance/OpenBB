---
title: delete
description: OpenBB's delete function page. The function takes the data and column
  parameters. There are no return values.
keywords:
- openbb.forecast.delete
- delete function
- data parameter
- column parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.delete - Reference | OpenBB SDK Docs" />

Delete a column from a dataframe

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L470)]

```python wordwrap
openbb.forecast.delete(data: pd.DataFrame, column: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to delete a column from | None | False |
| column | str | The column to delete | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| None |  |
---

