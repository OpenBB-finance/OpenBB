---
title: load
description: OpenBB Terminal Function
---

# load

Get historical data.

### Usage

```python
load --fund FUND [FUND ...] [-n] [-s START] [-e END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| fund | Fund string to search for | None | False | None |
| name | Flag to indicate name provided instead of symbol. | False | True | None |
| start | The starting date (format YYYY-MM-DD) of the fund | 2021-11-24 | True | None |
| end | The ending date (format YYYY-MM-DD) of the fund | 2022-11-25 | True | None |

---
