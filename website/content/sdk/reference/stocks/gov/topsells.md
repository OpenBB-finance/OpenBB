---
title: topsells
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# topsells

<Tabs>
<TabItem value="model" label="Model" default>

Get top sell government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L287)]

```python
openbb.stocks.gov.topsells(gov_type: str = "congress", past_transactions_months: int = 6)
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
| pd.DataFrame | DataFrame of top government sell trading |
---



</TabItem>
<TabItem value="view" label="Chart">

Top sell government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L151)]

```python
openbb.stocks.gov.topsells_chart(gov_type: str = "congress", past_transactions_months: int = 6, limit: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
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