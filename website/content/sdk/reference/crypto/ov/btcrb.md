---
title: btcrb
description: btcrb is a feature of the OpenBB Terminal that allows users to access
  historical bitcoin price data and view it in a rainbow chart. At its core, btcrb
  provides Python methods for retrieving this data over a specified date range and
  visualizing it using Matplotlib.
keywords:
- Bitcoin
- btcrb
- Price Data
- Rainbow Chart
- Data Retrieval
- Historical Bitcoin Data
- Matplotlib Visualization
- Cryptocurrency
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.btcrb - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get bitcoin price data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/glassnode_model.py#L19)]

```python
openbb.crypto.ov.btcrb(start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | price over time |
---

</TabItem>
<TabItem value="view" label="Chart">

Displays bitcoin rainbow chart

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/glassnode_view.py#L29)]

```python
openbb.crypto.ov.btcrb_chart(start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
