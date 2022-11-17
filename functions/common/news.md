---
title: news
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# news

<Tabs>
<TabItem value="model" label="Model" default>

## common_feedparser_model.get_news

```python title='openbb_terminal/common/feedparser_model.py'
def get_news(term: str, sources: str, sort: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/feedparser_model.py#L13)

Description: Get news for a given term and source. [Source: Feedparser]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | term to search on the news articles | None | False |
| sources | str | sources to exclusively show news from (separated by commas) | None | False |
| sort | str | the column to sort by | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| articles | dict | term to search on the news articles | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_feedparser_view.display_news

```python title='openbb_terminal/common/feedparser_view.py'
def display_news(term: str, sources: str, limit: int, export: str, sort: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/feedparser_view.py#L16)

Description: Display news for a given term and source. [Source: Feedparser]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | term to search on the news articles | None | False |
| sources | str | sources to exclusively show news from | None | False |
| limit | int | number of articles to display | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| sort | str | the column to sort by | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>