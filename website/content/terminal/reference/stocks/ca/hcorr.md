---
title: hcorr
description: The page presents a correlation heatmap 'hcorr' based on historical price
  comparison between similar companies. This tool assists in understanding and visualizing
  stock market trends.
keywords:
- hcorr
- correlation heatmap
- price comparison
- historical data
- stock market trends
- financial tools
- data visualization
- type_candle
- display_full_matrix
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /ca/hcorr - Reference | OpenBB Terminal Docs" />

Correlation heatmap based on historical price comparison between similar companies.

### Usage

```python wordwrap
hcorr [-t {o,h,l,c,a}] [-s START] [-e END] [--display-full-matrix]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| type_candle | -t  --type | Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close, r-returns. | a | True | o, h, l, c, a |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the stock | 2022-11-20 | True | None |
| end | -e  --end | The end date (format YYYY-MM-DD) of the stocks | 2023-11-21 | True | None |
| display_full_matrix | --display-full-matrix | Display all matrix values, rather than masking off half. | False | True | None |

![hcorr](https://user-images.githubusercontent.com/46355364/154073186-45336f5f-85e1-4cb9-9307-9694295b1f80.png)

---
