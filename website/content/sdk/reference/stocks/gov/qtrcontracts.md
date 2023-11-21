---
title: qtrcontracts
description: Documentation on the use of qtrcontracts function in Python for analyzing
  quarterly contracts by ticker. Posts include parameter details for the model and
  chart functions.
keywords:
- qtrcontracts function
- quarterly contracts analytics
- OpenBB finance
- Model function
- Chart function
- Parameter settings
- Source code
- matplotlib.axes._axes.Axes
- Total analysis
- Momentum analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.qtrcontracts - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Analyzes quarterly contracts by ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L484)]

```python wordwrap
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L477)]

```python wordwrap
openbb.stocks.gov.qtrcontracts_chart(analysis: str = "total", limit: int = 5, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| analysis | str | Analysis to perform.  Either 'total', 'upmom' 'downmom' | total | True |
| limit | int | Number to show | 5 | True |
| raw | bool | Flag to display raw data | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>