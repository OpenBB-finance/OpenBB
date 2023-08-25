---
title: hist
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hist

<Tabs>
<TabItem value="model" label="Model" default>

Get historical prices for all comparison stocks

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_model.py#L31)]

```python
openbb.stocks.ca.hist(similar: List[str], start_date: Optional[str] = None, candle_type: str = "a")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| candle_type | str | Candle variable to compare, by default "a" for Adjusted Close. Possible values are: o, h, l, c, a, v, r | a | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing candle type variable for each ticker |
---



</TabItem>
<TabItem value="view" label="Chart">

Display historical stock prices. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_view.py#L43)]

```python
openbb.stocks.ca.hist_chart(similar: List[str], start_date: Optional[str] = None, candle_type: str = "a", normalize: bool = True, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| candle_type | str | OHLCA column to use or R to use daily returns calculated from Adjusted Close, by default "a" for Adjusted Close | a | True |
| normalize | bool | Boolean to normalize all stock prices using MinMax defaults True | True | True |
| export | str | Format to export historical prices, by default "" |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>