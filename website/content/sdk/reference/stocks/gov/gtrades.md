---
title: gtrades
description: This page provides the documentation for the 'gtrades' function in OpenBB's
  terminal for stock traders. It contains two tabs - the 'model' tab explains how
  to get the government trading data for a specific ticker, while the 'view' tab provides
  instructions for displaying this data as a chart.
keywords:
- stock trading
- government trading data
- quiverquant.com
- gtrades function
- model
- view
- congress
- senate
- house
- trades chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.gtrades - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Government trading for specific ticker [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L418)]

```python wordwrap
openbb.stocks.gov.gtrades(symbol: str, gov_type: str = "congress", past_transactions_months: int = 6)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| past_transactions_months | int | Number of months to get transactions for | 6 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of tickers government trading |
---



</TabItem>
<TabItem value="view" label="Chart">

Government trading for specific ticker [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L350)]

```python wordwrap
openbb.stocks.gov.gtrades_chart(symbol: str, gov_type: str = "congress", past_transactions_months: int = 6, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| past_transactions_months | int | Number of months to get transactions for | 6 | True |
| raw | bool | Show raw output of trades | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>