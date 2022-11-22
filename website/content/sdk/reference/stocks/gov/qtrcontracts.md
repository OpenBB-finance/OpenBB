---
title: qtrcontracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# qtrcontracts

<Tabs>
<TabItem value="model" label="Model" default>

Analyzes quarterly contracts by ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L482)]

```python
openbb.stocks.gov.qtrcontracts(analysis: str = "total", limit: int = 5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| analysis | str | How to analyze.  Either gives total amount or sorts by high/low momentum. | total | True |
| limit | int | Number to return, by default 5 | 5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with tickers and total amount if total selected. |
---



</TabItem>
<TabItem value="view" label="Chart">

Quarterly contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L446)]

```python
openbb.stocks.gov.qtrcontracts_chart(analysis: str = "total", limit: int = 5, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| analysis | str | Analysis to perform.  Either 'total', 'upmom' 'downmom' | total | True |
| limit | int | Number to show | 5 | True |
| raw | bool | Flag to display raw data | False | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>