---
title: news
description: The page provides documentation on how to get and display news for a
  given term using OpenBB's Python functions. It also describes parameters used in
  these functions and links to the related source codes.
keywords:
- Documentation
- Python functions
- News retrieval
- NewsAPI
- Source code
- Parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.news - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get news for a given term. [Source: NewsAPI]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/newsapi_model.py#L20)]

```python wordwrap
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
| pd.DataFrame | DataFrame with columns Date, Description, URL |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing news for a given term. [Source: NewsAPI]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/newsapi_view.py#L17)]

```python wordwrap
openbb.etf.news_chart(query: str, limit: int = 10, start_date: Optional[str] = None, show_newest: bool = True, sources: str = "", export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | term to search on the news articles | None | False |
| start_date | Optional[str] | date to start searching articles from formatted YYYY-MM-DD | None | True |
| limit | int | number of articles to display | 10 | True |
| show_newest | bool | flag to show newest articles first | True | True |
| sources | str | sources to exclusively show news from |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>