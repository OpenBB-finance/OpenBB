---
title: historical
description: OpenBB Terminal Function
---

# historical

Historical price comparison between similar companies [Source: Yahoo Finance]

### Usage

```python
historical [-l LIMIT] [-n] [-s START] [-t {o,h,l,c,a}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of the most shorted stocks to retrieve. | 10 | True | None |
| no_scale | Flag to not put all prices on same 0-1 scale | False | True | None |
| start | The starting date (format YYYY-MM-DD) of the historical price to plot | 2022-05-29 | True | None |
| type_candle | type of candles: o-open, h-high, l-low, c-close, a-adjusted close. | a | True | o, h, l, c, a |

---
