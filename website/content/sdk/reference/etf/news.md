---
title: news
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# news

<Tabs>
<TabItem value="model" label="Model" default>

Get news for a given term. [Source: NewsAPI]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/newsapi_model.py#L18)]

```python
openbb.etf.news(query: str, limit: int = 10, start_date: Optional[str] = None, show_newest: bool = True, sources: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | term to search on the news articles | None | False |
| start_date | Optional[str] | date to start searching articles from formatted YYYY-MM-DD | None | True |
| show_newest | bool | flag to show newest articles first | True | True |
| sources | str | sources to exclusively show news from (comma separated) |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[Tuple[pd.DataFrame, dict]] | List of tuples containing news df in first index,<br/>dict containing title of news df. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing news for a given term. [Source: NewsAPI]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/newsapi_view.py#L20)]

```python
openbb.etf.news_chart(query: str, limit: int = 3, start_date: Optional[str] = None, show_newest: bool = True, sources: str = "", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | term to search on the news articles | None | False |
| start_date | Optional[str] | date to start searching articles from formatted YYYY-MM-DD | None | True |
| limit | int | number of articles to display | 3 | True |
| show_newest | bool | flag to show newest articles first | True | True |
| sources | str | sources to exclusively show news from |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>