---
title: hcorr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hcorr

<Tabs>
<TabItem value="model" label="Model" default>

Get historical price correlation. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_model.py#L98)]

```python
openbb.stocks.ca.hcorr(similar: List[str], start_date: Optional[str] = None, candle_type: str = "a")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| candle_type | str | OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close | a | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Dataframe with correlation matrix, Dataframe with historical prices for all comparison stocks |
---



</TabItem>
<TabItem value="view" label="Chart">

Correlation heatmap based on historical price comparison

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_view.py#L159)]

```python
openbb.stocks.ca.hcorr_chart(similar: List[str], start_date: Optional[str] = None, candle_type: str = "a", display_full_matrix: bool = False, raw: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| candle_type | str | OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close | a | True |
| display_full_matrix | bool | Optionally display all values in the matrix, rather than masking off half, by default False | False | True |
| raw | bool | Whether to display raw data | False | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |
| export | str | Format to export correlation prices, by default "" |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>