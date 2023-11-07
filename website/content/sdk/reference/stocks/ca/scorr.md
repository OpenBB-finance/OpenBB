---
title: scorr
description: This page provides information on the 'scorr' function, a tool used to
  get correlation sentiments across similar companies. It also displays information
  on how to utilize the 'scorr_chart' function, designed to plot correlation sentiments
  heatmap for a set of similar companies.
keywords:
- scorr function
- scorr_chart function
- correlation sentiments
- similar companies
- FinBrain
- FinViz
- Finnhub
- Polygon
- heatmap plot
- sentiment analysis
- stock comparison
- matplotlib axes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.scorr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get correlation sentiments across similar companies. [Source: FinBrain].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_model.py#L125)]

```python
openbb.stocks.ca.scorr(similar: List[str])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | Similar companies to compare income with.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame,pd.DataFrame] | Contains sentiment analysis from several tickers |
---

</TabItem>
<TabItem value="view" label="Chart">

Plot correlation sentiments heatmap across similar companies. [Source: FinBrain].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_view.py#L121)]

```python
openbb.stocks.ca.scorr_chart(similar: List[str], raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | Similar companies to compare income with.<br/>Comparable companies can be accessed through<br/>finviz_peers(), finnhub_peers() or polygon_peers(). | None | False |
| raw | bool | Output raw values, by default False | False | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
