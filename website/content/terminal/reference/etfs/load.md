---
title: load
description: OpenBB Terminal Function
---

# load

Load ETF ticker to perform analysis on.

### Usage

```python
usage: load -t TICKER [-s START] [-e END] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ticker | ETF ticker | None | False | None |
| start | The starting date (format YYYY-MM-DD) of the ETF | 2021-11-21 | True | None |
| end | The ending date (format YYYY-MM-DD) of the ETF | 2022-11-22 | True | None |
| limit | Limit of holdings to display | 5 | True | None |
---

