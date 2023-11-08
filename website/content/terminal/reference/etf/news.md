---
title: news
description: The page provides information on how to print the latest news about ETF
  using parameters such as limit, starting date, order of articles, and news sources.
  This information is sourced from the News API.
keywords:
- ETF
- News API
- latest news
- articles
- bbc
- yahoo.com
- docusaurus
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf /news - Reference | OpenBB Terminal Docs" />

Prints latest news about ETF, including date, title and web link. [Source: News API]

### Usage

```python
news [-l LIMIT] [-d N_START_DATE] [-o] [-s SOURCES]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of latest news being printed. | 5 | True | None |
| n_start_date | The starting date (format YYYY-MM-DD) to search articles from | datetime.now() - timedelta(days=365) | True | None |
| n_oldest | Show oldest articles first | True | True | None |
| sources | Show news only from the sources specified (e.g bbc yahoo.com) |  | True | None |

---
