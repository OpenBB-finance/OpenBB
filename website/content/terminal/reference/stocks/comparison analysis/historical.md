---
title: historical
description: OpenBB Terminal Function
---

# historical

Historical price comparison between similar companies.

### Usage

```python
usage: historical [-t {o,h,l,c,a}] [-n] [-s START]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| type_candle | Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. | a | True | o, h, l, c, a |
| normalize | Flag to normalize all prices on same 0-1 scale | False | True | None |
| start | The starting date (format YYYY-MM-DD) of the stock | 2021-11-21 | True | None |
---

