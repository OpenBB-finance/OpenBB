---
title: sentiment
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sentiment

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ca_finbrain_model.get_sentiments

```python title='openbb_terminal/stocks/comparison_analysis/finbrain_model.py'
def get_sentiments(symbols: List[str]) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_model.py#L47)

Description: Gets Sentiment analysis from several symbols provided by FinBrain's API

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of tickers to get sentiment
Comparable companies can be accessed through
finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Contains sentiment analysis from several tickers |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ca_finbrain_view.display_sentiment_compare

```python title='openbb_terminal/stocks/comparison_analysis/finbrain_view.py'
def display_sentiment_compare(similar: List[str], raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_view.py#L32)

Description: Display sentiment for all ticker. [Source: FinBrain]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | Similar companies to compare income with.
Comparable companies can be accessed through
finviz_peers(), finnhub_peers() or polygon_peers(). | None | False |
| raw | bool | Output raw values, by default False | False | True |
| export | str | Format to export data | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>