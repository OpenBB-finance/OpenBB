---
title: scorr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# scorr

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