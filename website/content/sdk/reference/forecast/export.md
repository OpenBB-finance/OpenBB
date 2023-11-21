---
title: export
description: Enhance your grasp of the openbb.forecast.export function from the OpenBBTerminal,
  which is employed to export forecasting data. This function takes no parameters
  and does not return anything. Chances to learn more about Python source code.
keywords:
- openbb.forecast.export
- forecasting
- data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.export - Reference | OpenBB SDK Docs" />

Export a dataframe to a file

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L317)]

```python wordwrap
openbb.forecast.export(data: pd.DataFrame, export: str, name: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to export | None | False |
| export | str | The format to export the dataframe to | None | False |
| name | str | The name of the dataframe |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |


---

## Returns

This function does not return anything

---

