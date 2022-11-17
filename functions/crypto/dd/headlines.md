---
title: headlines
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# headlines

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_finbrain_model.get_sentiment

```python title='openbb_terminal/common/behavioural_analysis/finbrain_model.py'
def get_sentiment(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/finbrain_model.py#L15)

Description: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get the sentiment analysis from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame() | Empty if there was an issue with data retrieval |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_crypto_finbrain_view.display_crypto_sentiment_analysis

```python title='openbb_terminal/cryptocurrency/due_diligence/finbrain_crypto_view.py'
def display_crypto_sentiment_analysis(symbol: str, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/finbrain_crypto_view.py#L39)

Description: Sentiment analysis from FinBrain for Cryptocurrencies

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency | None | False |
| raw | False | Display raw table data | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>