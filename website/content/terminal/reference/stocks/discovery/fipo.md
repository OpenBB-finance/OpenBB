---
title: fipo
description: OpenBB Terminal Function
---

# fipo

Future IPOs dates. [Source: https://finnhub.io]

### Usage

```python
usage: fipo [-d DAYS] [-s END] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| days | Number of days in the future to look for IPOs. | 5 | True | None |
| end | The end date (format YYYY-MM-DD) to look for IPOs, starting from today. When set, end date will override --days argument | None | True | None |
| limit | Limit number of IPOs to display. | 20 | True | None |
---

