---
title: fred
description: The page includes detailed information on the 'fred' function in the
  OpenBBTerminal software. With this function, users can acquire and visualize economic
  series data from the Federal Reserve Economic Data (FRED) database. It also lists
  out function parameters and return type.
keywords:
- fred function
- Federal Reserve Economic Data
- FRED
- economy
- series data
- parameters
- return type
- visualization
- code
- metadata
- data retrieval
- data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.fred - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get Series data. [Source: FRED]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L208)]

```python
openbb.economy.fred(series_ids: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_ids | List[str] | Series ID to get data from | None | False |
| start_date | str | Start date to get data from, format yyyy-mm-dd | None | True |
| end_date | str | End data to get from, format yyyy-mm-dd | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Series data |
---

</TabItem>
<TabItem value="view" label="Chart">

Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_view.py#L76)]

```python
openbb.economy.fred_chart(series_ids: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 10, get_data: bool = False, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_ids | List[str] | FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3 | None | False |
| start_date | Optional[str] | Starting date (YYYY-MM-DD) of data | None | True |
| end_date | Optional[str] | Ending date (YYYY-MM-DD) of data | None | True |
| limit | int | Number of data points to display. | 10 | True |
| raw | bool | Output only raw data | False | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
