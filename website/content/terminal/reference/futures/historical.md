---
title: historical
description: OpenBB Terminal Function
---

# historical

Display futures historical. [Source: YahooFinance]

### Usage

```python
usage: historical -t TICKER [-s START] [-e EXPIRY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ticker | Future ticker to display timeseries separated by comma when multiple, e.g.: BLK,QI |  | False | None |
| start | Initial date. Default: 3 years ago | datetime.now() - timedelta(days=365) | True | None |
| expiry | Select future expiry date with format YYYY-MM |  | True | None |
---

