---
title: hist
description: Python code examples using OpenBB Terminal to retrieve, visualize and
  manipulate historical stock prices from Yahoo Finance for a list of comparison stocks.
  The code covers data acquisition, charting of historical prices, and export functionalities.
keywords:
- stock comparison
- historical stock prices
- data visualization
- Python code
- Yahoo Finance
- stock market analysis
- stock price chart
- stock data export
- data manipulation
- stock data normalization
- Comparable companies
- Finnhub peers
- Finnviz peers
- Polygon peers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.hist - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical prices for all comparison stocks

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_model.py#L31)]

```python wordwrap
openbb.stocks.ca.hist(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, candle_type: str = "a")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end_date | Optional[str] | End date (e.g., 2023-01-01). None defaults to today | None | True |
| candle_type | str | Candle variable to compare, by default "a" for Adjusted Close. Possible values are: o, h, l, c, a, v, r | a | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical prices for all comparison stocks |
---

## Examples

```python
from openbb_terminal.sdk import openbb
```

```
Start by getting similar tickers from finviz for AAPL
```
```python
similar = openbb.stocks.comparison_analysis.finviz_peers("AAPL")
hist_df = openbb.stocks.ca.hist(similar)
```

```
We can specify a start date and an end date
```
```python
hist_df_2022 = openbb.stocks.ca.hist(similar, start_date="2022-01-01", end_date="2022-12-31")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display historical stock prices. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_view.py#L35)]

```python wordwrap
openbb.stocks.ca.hist_chart(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, candle_type: str = "a", normalize: bool = True, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end_date | Optional[str] | End date (e.g., 2023-01-01) | None | True |
| candle_type | str | OHLCA column to use or R to use daily returns calculated from Adjusted Close, by default "a" for Adjusted Close | a | True |
| normalize | bool | Boolean to normalize all stock prices using MinMax defaults True | True | True |
| export | str | Format to export historical prices, by default "" |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>