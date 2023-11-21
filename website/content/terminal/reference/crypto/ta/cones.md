---
title: cones
description: Calculates the realized volatility quantiles over rolling windows of time
keywords:
- crypto.ta
- cones
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /ta/cones - Reference | OpenBB Terminal Docs" />

Calculates the realized volatility quantiles over rolling windows of time. The model for calculating volatility is selectable.

### Usage

```python wordwrap
cones [-l LOWER_Q] [-u UPPER_Q] [-m {STD,Parkinson,Garman-Klass,Hodges-Tompkins,Rogers-Satchell,Yang-Zhang}] [--is_crypto]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| lower_q | -l  --lower_q | The lower quantile value for calculations. | 0.25 | True | None |
| upper_q | -u  --upper_q | The upper quantile value for calculations. | 0.75 | True | None |
| model | -m  --model | The model used to calculate realized volatility. | STD | True | STD, Parkinson, Garman-Klass, Hodges-Tompkins, Rogers-Satchell, Yang-Zhang |
| is_crypto | --is_crypto | If True, volatility is calculated for 365 days instead of 252. | True | True | None |

---
