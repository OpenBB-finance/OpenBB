---
title: mktcap
description: This page provides documentation about the mktcap function of OpenBB-finance's
  Yahoo Finance Module. It explains the operation and usage of the functions for
  market cap modeling and charting over a certain period.
keywords:
- OpenBB-finance
- Yahoo Finance
- mktcap function
- market cap model
- market cap chart
- Stock ticker symbol
- Financial analysis
- Fundamental analysis
- Stock market data
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.mktcap - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get market cap over time for ticker. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L195)]

```python wordwrap
openbb.stocks.fa.mktcap(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get market cap over time | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 3 years back | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of estimated market cap over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Display market cap over time. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L270)]

```python wordwrap
openbb.stocks.fa.mktcap_chart(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). If not provided, the earliest date available is used. | None | True |
| end_date | Optional[str] | End date (e.g., 2021-10-01). If not provided, the latest date available is used. | None | True |
| raw | bool | Whether to return the raw data or not | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>