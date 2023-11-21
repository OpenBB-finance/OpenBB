---
title: topsells
description: Explore the topsells documentation page for detailed instructions on
  how to use the openbb.stocks.gov.topsells function. This function is used to get
  top sell government trading data from quiverquant.com. It covers different types
  of government data including congress, senate, and house. The function allows for
  customization such as defining the number of past transaction months. Samples of
  source codes are also provided with relevant links for reference.
keywords:
- topsells
- trading
- government data
- quiverquant.com
- openbb.stocks.gov
- congress
- senate
- house
- past transactions months
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.topsells - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get top sell government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L285)]

```python wordwrap
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L160)]

```python wordwrap
openbb.stocks.gov.topsells_chart(gov_type: str = "congress", past_transactions_months: int = 6, limit: int = 10, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| past_transactions_months | int | Number of months to get trading for | 6 | True |
| limit | int | Number of tickers to show | 10 | True |
| raw | bool | Display raw data | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>