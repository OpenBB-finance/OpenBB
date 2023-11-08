---
title: sentiment
description: The page provides detailed information about Sentiment Analysis functions
  provided by the OpenBB Finance Terminal. It guides users on how to retrieve sentiment
  analysis for several symbols using FinBrain's API and how to display the sentiment
  for all ticker.
keywords:
- API
- Sentiment Analysis
- Finance
- Terminal
- FinBrain
- Ticker
- Symbols
- Finviz_peers
- Finnhub_peers
- Polygon_peers
- Data visualization
- matplotlib
- Data Export
- Sentiment chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.sentiment - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gets Sentiment analysis from several symbols provided by FinBrain's API.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_model.py#L47)]

```python
openbb.stocks.ca.sentiment(symbols: List[str])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of tickers to get sentiment.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Contains sentiment analysis from several tickers |
---

</TabItem>
<TabItem value="view" label="Chart">

Display sentiment for all ticker. [Source: FinBrain].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_view.py#L32)]

```python
openbb.stocks.ca.sentiment_chart(similar: List[str], raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
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
