---
title: news
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# news

<Tabs>
<TabItem value="model" label="Model" default>

Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/cryptopanic_model.py#L158)]

```python
openbb.crypto.dd.news(limit: int = 60, post_kind: str = "news", filter_: Optional[str] = None, region: str = "en", source: Optional[str] = None, symbol: Optional[str] = None, sortby: str = "published_at", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | number of news to fetch | 60 | True |
| post_kind | str | Filter by category of news. Available values: news or media. | news | True |
| filter_ | Optional[str] | Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol | None | True |
| region | str | Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),<br/>es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский) | en | True |
| sortby | str | Key to sort by. | published_at | True |
| ascend | bool | Sort in ascend order. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with recent news from different sources filtered by provided parameters. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing recent posts from CryptoPanic news aggregator platform.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/cryptopanic_view.py#L18)]

```python
openbb.crypto.dd.news_chart(post_kind: str = "news", region: str = "en", filter_: Optional[str] = None, source: Optional[str] = None, symbol: Optional[str] = None, limit: int = 25, ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | number of news to display | 25 | True |
| post_kind | str | Filter by category of news. Available values: news or media. | news | True |
| filter_ | Optional[str] | Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol | None | True |
| region | str | Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),<br/>es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский) | en | True |
| ascend | bool | Sort in ascending order. | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>