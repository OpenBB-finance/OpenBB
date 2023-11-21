---
title: news
description: Get news for a given term and source
keywords:
- stocks
- news
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.news - Reference | OpenBB SDK Docs" />

Get news for a given term and source. [Source: Ultima Insights News Monitor]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/ultima_newsmonitor_model.py#L26)]

```python wordwrap
openbb.stocks.news(term: str = "", sort: str = "articlePublishedDate")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | term to search on the news articles |  | True |
| sort | str | the column to sort by | articlePublishedDate | True |


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

