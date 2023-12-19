---
title: topbuys
description: This documentation page covers the top buy government trading on OpenBB
  Terminal, providing detailed information on relevant python functions and parameters.
  It features source code and explanations for different data types and optional parameters.
keywords:
- top buy government trading
- python functions
- parameters
- data types
- quiverquant.com
- congress
- senate
- house
- pandas DataFrame
- matplotlib
- trading data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.topbuys - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get top buy government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L227)]

```python
openbb.stocks.gov.topbuys(gov_type: str = "congress", past_transactions_months: int = 6)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| past_transactions_months | int | Number of months to get trading for | 6 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of top government buy trading |
---

</TabItem>
<TabItem value="view" label="Chart">

Top buy government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L79)]

```python
openbb.stocks.gov.topbuys_chart(gov_type: str = "congress", past_transactions_months: int = 6, limit: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| past_transactions_months | int | Number of months to get trading for | 6 | True |
| limit | int | Number of tickers to show | 10 | True |
| raw | bool | Display raw data | False | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
