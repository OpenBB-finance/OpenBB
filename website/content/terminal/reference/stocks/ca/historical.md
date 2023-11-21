---
title: historical
description: A guide for understanding and using the 'historical' feature for price
  comparison between similar companies, includes usage, parameters details and graphical
  representation.
keywords:
- Price comparison
- Historical prices
- Stock analysis
- Normalization
- Candle data
- Starting date
- High, low, close prices
- Company comparison
- Open-high-low-close
- Adjusted close
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /ca/historical - Reference | OpenBB Terminal Docs" />

Historical price comparison between similar companies.

### Usage

```python wordwrap
historical [-t {o,h,l,c,a}] [-n] [-s START] [-e END]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| type_candle | -t  --type | Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. | a | True | o, h, l, c, a |
| normalize | -n  --normalize | Flag to normalize all prices on same 0-1 scale | False | True | None |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the stocks | 2022-11-20 | True | None |
| end | -e  --end | The end date (format YYYY-MM-DD) of the stocks | 2023-11-21 | True | None |

![historical](https://user-images.githubusercontent.com/46355364/154073378-935eddd4-167e-48e8-9e3d-34029e5ba42f.png)

---
