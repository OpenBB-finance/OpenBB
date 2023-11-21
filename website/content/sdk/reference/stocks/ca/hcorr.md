---
title: hcorr
description: The page gives detailed guidelines on how to use the hcorr function in
  OpenBB Terminal to gather historical price correlation data. It further explains
  the process to create correlation heatmaps based on historical price comparison.
keywords:
- historical price correlation
- chart
- finance tools
- correlation matrix
- finance source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.hcorr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical price correlation. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_model.py#L116)]

```python wordwrap
openbb.stocks.ca.hcorr(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, candle_type: str = "a")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to today | None | True |
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/yahoo_finance_view.py#L154)]

```python wordwrap
openbb.stocks.ca.hcorr_chart(similar: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, candle_type: str = "a", display_full_matrix: bool = False, raw: bool = False, external_axes: bool = False, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of similar tickers.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 1 year back | None | True |
| end_date | Optional[str] | End date (e.g., 2023-01-01) | None | True |
| candle_type | str | OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close | a | True |
| display_full_matrix | bool | Optionally display all values in the matrix, rather than masking off half, by default False | False | True |
| raw | bool | Whether to display raw data | False | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |
| export | str | Format to export correlation prices, by default "" |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>