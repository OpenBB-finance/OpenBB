---
title: vwap
description: This documentation page provides detailed information about the volume
  weighted average price, or VWAP, a popular technical analysis indicator. It includes
  Python code examples for calculating VWAP on a pandas DataFrame of stocks prices,
  and creating a visual chart of VWAP data using matplotlib.
keywords:
- vwap
- technical analysis
- volume weighted average price
- data visualization
- pandas dataframe
- stock prices
- trading indicators
- OHLC prices
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.vwap - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gets volume weighted average price (VWAP)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L139)]

```python
openbb.ta.vwap(data: pd.DataFrame, offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of dates and prices | None | False |
| offset | int | Length of offset | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with VWAP data |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots VWMA technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_view.py#L133)]

```python
openbb.ta.vwap_chart(data: pd.DataFrame, symbol: str = "", start_date: Optional[str] = None, end_date: Optional[str] = None, offset: int = 0, interval: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| symbol | str | Ticker |  | True |
| offset | int | Offset variable | 0 | True |
| start_date | Optional[str] | Initial date, format YYYY-MM-DD | None | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| interval | str | Interval of data |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
