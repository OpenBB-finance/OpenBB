---
title: news
description: OpenBB Terminal Function
---

# news

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
