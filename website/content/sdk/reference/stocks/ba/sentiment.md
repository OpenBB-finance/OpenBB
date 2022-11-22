---
title: sentiment
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sentiment

<Tabs>
<TabItem value="model" label="Model" default>

Get sentiments from symbol.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/twitter_model.py#L125)]

```python
openbb.stocks.ba.sentiment(symbol: str, n_tweets: int = 15, n_days_past: int = 2)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol to get sentiment for | None | False |
| n_tweets | int | Number of tweets to get per hour | 15 | True |
| n_days_past | int | Number of days to extract tweets for | 2 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of sentiment |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots sentiments from symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/twitter_view.py#L79)]

```python
openbb.stocks.ba.sentiment_chart(symbol: str, n_tweets: int = 15, n_days_past: int = 2, compare: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol to get sentiment for | None | False |
| n_tweets | int | Number of tweets to get per hour | 15 | True |
| n_days_past | int | Number of days to extract tweets for | 2 | True |
| compare | bool | Show corresponding change in stock price | False | True |
| export | str | Format to export tweet dataframe |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>