---
title: mentions
description: Documentation page for OpenBB Terminal's modules 'mentions' and 'mentions_chart.'
  These modules analyze and visualize the interest over time for a particular stock's
  symbol using Google's API.
keywords:
- Stock market analysis
- Google API
- Stock interest
- Data visualization
- Finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.mentions - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get interest over time from google api [Source: google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L16)]

```python wordwrap
openbb.stocks.ba.mentions(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of interest over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_view.py#L19)]

```python wordwrap
openbb.stocks.ba.mentions_chart(symbol: str, start_date: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| start_date | str | Start date as YYYY-MM-DD string |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>