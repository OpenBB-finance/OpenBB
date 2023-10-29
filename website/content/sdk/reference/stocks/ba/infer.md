---
title: infer
description: This page is a detailed guide for using OpenBB's terminal to access and
  analyze Twitter data, providing tips for inferring market sentiment from tweets
  and visualizing data.
keywords:
- terminal guidance
- Twitter data analysis
- market sentiment
- social media analytics
- VADER sentiment analysis
- data visualization
- programming code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.infer - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Load tweets from twitter API and analyzes using VADER.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/twitter_model.py#L23)]

```python
openbb.stocks.ba.infer(symbol: str, limit: int = 100, start_date: Optional[str] = "", end_date: Optional[str] = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to search twitter for | None | False |
| limit | int | Number of tweets to analyze | 100 | True |
| start_date | Optional[str] | If given, the start time to get tweets from |  | True |
| end_date | Optional[str] | If given, the end time to get tweets from |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of tweets and sentiment |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints Inference sentiment from past n tweets.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/twitter_view.py#L29)]

```python
openbb.stocks.ba.infer_chart(symbol: str, limit: int = 100, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of tweets to analyze | 100 | True |
| export | str | Format to export tweet dataframe |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
