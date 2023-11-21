---
title: volume
description: This documentation page details how to get and display stock volume using
  openbb.stocks.ca volume function. Includes Python codes and parameter descriptions
  for user guidance.
keywords:
- openbb.stocks.ca
- stock volume
- Yahoo Finance
- docusaurus
- parameter description
- volume_chart
- volume function
- stock analysis
- finnhub_peers
- finviz_peers
- polygon_peers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.volume - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get stock volume. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_model.py#L155)]

```python wordwrap
openbb.stocks.ca.volume(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end_date | Optional[str] | End date (e.g., 2023-01-01). None defaults to today | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with volume for stock |
---



</TabItem>
<TabItem value="view" label="Chart">

Display stock volume. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_view.py#L104)]

```python wordwrap
openbb.stocks.ca.volume_chart(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end_date | Optional[str] | End date (e.g., 2023-01-01). Defaults to today | None | True |
| export | str | Format to export historical prices, by default "" |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>