---
title: histcont
description: This page provides documentation on OpenBBTerminal's histcont function.
  The function allows users to get and visualize historical quarterly government contracts.
keywords:
- histcont function
- historical quarterly government contracts
- quiverquant.com
- stock data
- financial data
- data visualization
- ticker symbol
- congress trading data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.histcont - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical quarterly government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L137)]

```python wordwrap
openbb.stocks.gov.histcont(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical quarterly government contracts |
---



</TabItem>
<TabItem value="view" label="Chart">

Show historical quarterly government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L598)]

```python wordwrap
openbb.stocks.gov.histcont_chart(symbol: str, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |
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