---
title: lastcontracts
description: This documentation page provides information on using OpenBBTerminal's
  Python code to obtain government contract data from QuiverQuant. It guides how to
  use the lastcontracts model and view functions for data analysis and export.
keywords:
- Government contracts
- QuiverQuant
- Data analysis
- Finance
- Source code
- Data export
- GitHub
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.lastcontracts - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get last government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L379)]

```python wordwrap
openbb.stocks.gov.lastcontracts(past_transaction_days: int = 2)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | 2 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of government contracts |
---



</TabItem>
<TabItem value="view" label="Chart">

Last government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L243)]

```python wordwrap
openbb.stocks.gov.lastcontracts_chart(past_transaction_days: int = 2, limit: int = 20, sum_contracts: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | 2 | True |
| limit | int | Number of contracts to show | 20 | True |
| sum_contracts | bool | Flag to show total amount of contracts given out. | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>