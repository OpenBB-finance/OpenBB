---
title: news
description: This documentation page provides detailed information on how to retrieve
  news articles using the OpenBBTerminal's function 'openbb.news'. The function allows
  users to specify search terms, sources, and sorting parameters. Examples of using
  the function are also provided.
keywords:
- News
- Feedparser
- Source Code
- openbb news
- News Article Search
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="news - Reference | OpenBB SDK Docs" />

Get news for a given term and source. [Source: Feedparser]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/feedparser_model.py#L13)]

```python
openbb.news(term: str = "", sources: str = "", sort: str = "published")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | term to search on the news articles |  | True |
| sources | str | sources to exclusively show news from (separated by commas) |  | True |
| sort | str | the column to sort by | published | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | term to search on the news articles |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.news()
```

---
