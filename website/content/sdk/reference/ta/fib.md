---
title: fib
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fib

<Tabs>
<TabItem value="model" label="Model" default>

Calculate Fibonacci levels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/custom_indicators_model.py#L17)]

```python
openbb.ta.fib(data: pd.DataFrame, limit: int = 120, start_date: Any = None, end_date: Any = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of prices | None | False |
| limit | int | Days to look back for retracement | 120 | True |
| start_date | Any | Custom start date for retracement | None | True |
| end_date | Any | Custom end date for retracement | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of fib levels |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots Calculated fibonacci retracement levels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/custom_indicators_view.py#L29)]

```python
openbb.ta.fib_chart(data: pd.DataFrame, limit: int = 120, start_date: Optional[str] = None, end_date: Optional[str] = None, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | OHLC data | None | False |
| limit | int | Days to lookback | 120 | True |
| start_date | Optional[str, None] | User picked date for starting retracement | None | True |
| end_date | Optional[str, None] | User picked date for ending retracement | None | True |
| symbol | str | Ticker symbol |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>