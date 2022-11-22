---
title: hcorr
description: OpenBB Terminal Function
---

# hcorr

Correlation heatmap based on historical price comparison between similar companies.

### Usage

```python
usage: hcorr [-t {o,h,l,c,a}] [-s START] [--display-full-matrix]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| type_candle | Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close, r-returns. | a | True | o, h, l, c, a |
| start | The starting date (format YYYY-MM-DD) of the stock | 2021-11-21 | True | None |
| display_full_matrix | Display all matrix values, rather than masking off half. | False | True | None |
---

