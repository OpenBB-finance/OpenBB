---
title: news
description: Access news from either feedparser or biztoc for a given term or from specified sources
keywords:
- news
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title=".news - Reference | OpenBB SDK Docs" />

Access news from either feedparser or biztoc for a given term or from specified sources

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/news_sdk_helper.py#L9)]

```python wordwrap
openbb.root.news(term: str = "", sources: str = "", tag: Any = "", source: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | Term to sort for, by default "" |  | True |
| sources | str | News sources to include, by default "" |  | True |
| tag | str | Biztoc only selection for searching by a given tag, by default "" |  | True |
| source | str | Data provider, can be either FeedParser or BizToc.  Will default to Biztoc if key is provided |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of news |
---

