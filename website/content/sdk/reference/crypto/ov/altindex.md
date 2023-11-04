---
title: altindex
description: Page featuring the altindex function of the OpenBB library, enabling
  the tracking of altcoin performance over various periods of time.
keywords:
- altindex
- altcoin tracking
- cryptocurrency
- altcoin index
- Python crypto library
- blockchain documentation
- crypto charting
- scripting
- crypto data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.altindex - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get altcoin index overtime

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/blockchaincenter_model.py#L20)]

```python
openbb.crypto.ov.altindex(period: int = 30, start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| period | int | Number of days {30,90,365} to check performance of coins and calculate the altcoin index.<br/>E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),<br/>30 will check monthly performance (30 days). | 30 | True |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Date, Value (Altcoin Index) |
---

</TabItem>
<TabItem value="view" label="Chart">

Displays altcoin index overtime

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/blockchaincenter_view.py#L27)]

```python
openbb.crypto.ov.altindex_chart(period: int = 365, start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| period | int | Number of days to check the performance of coins and calculate the altcoin index.<br/>E.g., 365 will check yearly performance , 90 will check seasonal performance (90 days),<br/>30 will check monthly performance (30 days). | 365 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
