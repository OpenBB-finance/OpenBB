---
title: rot
description: This webpage contains detailed methods and code snippets to retrieve
  and visualize rating over time data for any stock ticker. It includes functioning
  code in Python, and links to the source code in GitHub.
keywords:
- stock ratings
- Finnhub api
- data visualization
- open source
- stock market
- financial markets
- investment research
- due diligence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.rot - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get rating over time data. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/finnhub_model.py#L17)]

```python
openbb.stocks.dd.rot(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get ratings from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with ratings |
---

</TabItem>
<TabItem value="view" label="Chart">

Rating over time (monthly). [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/finnhub_view.py#L75)]

```python
openbb.stocks.dd.rot_chart(symbol: str, limit: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | Ticker to get ratings from | None | True |
| limit | int | Number of last months ratings to show | 10 | True |
| raw | bool | Display raw data only | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
