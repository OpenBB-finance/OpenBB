---
title: _make_request
description: This is a documentation page for the '_make_request' helper method used
  for scraping in Python. The method takes a URL as parameter and returns a BeautifulSoup
  object or None.
keywords:
- make_request
- scraping
- code
- BeautifulSoup
- URL
- helper method
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss._make_request - Reference | OpenBB SDK Docs" />

Helper method to scrap.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_model.py#L67)]

```python
openbb.alt.oss._make_request(url: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| url | str | url to scrape | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[BeautifulSoup, None] | BeautifulSoup object or None |
---
