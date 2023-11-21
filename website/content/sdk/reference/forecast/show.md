---
title: show
description: Detailed documentation of OpenBB finance's 'show' and 'show_chart' functions.
  Learn how to effectively use these functions in your data analysis with clear instructions
  and direct source code links.
keywords:
- OpenBB finance
- Documentation
- Programming
- show function
- show_chart function
- Source Code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.show - Reference | OpenBB SDK Docs" />

Show a dataframe in a table

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L226)]

```python wordwrap
openbb.forecast.show(data: pd.DataFrame, limit: int = 15, limit_col: int = 10, name: str = "", export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to show | None | False |
| limit | int | The number of rows to show | 15 | True |
| limit_col | int | The number of columns to show | 10 | True |
| name | str | The name of the dataframe |  | True |
| export | str | Format to export data |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |


---

## Returns

This function does not return anything

---

