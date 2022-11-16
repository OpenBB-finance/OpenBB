---
title: scorr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# scorr

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ca_finbrain_model.get_sentiment_correlation

```python title='openbb_terminal/stocks/comparison_analysis/finbrain_model.py'
def get_sentiment_correlation(similar: List[str]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_model.py#L125)

Description: Get correlation sentiments across similar companies. [Source: FinBrain]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | Similar companies to compare income with.
Comparable companies can be accessed through
finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ca_finbrain_view.display_sentiment_correlation

```python title='openbb_terminal/stocks/comparison_analysis/finbrain_view.py'
def display_sentiment_correlation(similar: List[str], raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finbrain_view.py#L122)

Description: Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]

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