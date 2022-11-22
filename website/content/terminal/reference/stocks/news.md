---
title: news
description: OpenBB Terminal Function
---

# news

latest news of the company

### Usage

```python
usage: news [-d N_START_DATE] [-o] [-s SOURCES]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_start_date | The starting date (format YYYY-MM-DD) to search articles from | datetime.now() - timedelta(days=365) | True | None |
| n_oldest | Show oldest articles first | True | True | None |
| sources | Show news only from the sources specified (e.g bloomberg,reuters) |  | True | None |
---

