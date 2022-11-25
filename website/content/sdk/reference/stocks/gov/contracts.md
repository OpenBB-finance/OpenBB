---
title: contracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# contracts

<Tabs>
<TabItem value="model" label="Model" default>

Get government contracts for ticker [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L103)]

```python
openbb.stocks.gov.contracts(symbol: str, past_transaction_days: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get congress trading data from | None | False |
| past_transaction_days | int | Number of days to get transactions for | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most recent transactions by members of U.S. Congress |
---



</TabItem>
<TabItem value="view" label="Chart">

Show government contracts for ticker [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L380)]

```python
openbb.stocks.gov.contracts_chart(symbol: str, past_transaction_days: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get congress trading data from | None | False |
| past_transaction_days | int | Number of days to get transactions for | 10 | True |
| raw | bool | Flag to display raw data | False | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>