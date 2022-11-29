---
title: hist
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hist

<Tabs>
<TabItem value="model" label="Model" default>

Get hour-level sentiment data for the chosen symbol.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/sentimentinvestor_model.py#L19)]

```python
openbb.stocks.ba.hist(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, number: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to view sentiment data | None | False |
| start_date | Optional[str] | Initial date like string or unix timestamp (e.g. 12-21-2021) | None | True |
| end_date | Optional[str] | End date like string or unix timestamp (e.g. 12-21-2021) | None | True |
| number | int | Number of results returned by API call<br/>Maximum 250 per api call | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical sentiment |
---



</TabItem>
<TabItem value="view" label="Chart">

Display historical sentiment data of a ticker,

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/sentimentinvestor_view.py#L30)]

```python
openbb.stocks.ba.hist_chart(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, number: int = 100, raw: bool = False, limit: int = 10, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to view sentiment data | None | False |
| start_date | Optional[str] | Initial date like string or unix timestamp (e.g. 2021-12-21) | None | True |
| end_date | Optional[str] | End date like string or unix timestamp (e.g. 2022-01-15) | None | True |
| number | int | Number of results returned by API call<br/>Maximum 250 per api call | 100 | True |
| raw | boolean | Whether to display raw data, by default False | False | True |
| limit | int | Number of results display on the terminal<br/>Default: 10 | 10 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>