---
title: ccpi
description: Inflation is measured in terms of the annual growth rate and in index, 2015 base year with a breakdown for food, energy and total excluding food and energy
keywords:
- economy
- ccpi
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /ccpi - Reference | OpenBB Terminal Docs" />

Inflation is measured in terms of the annual growth rate and in index, 2015 base year with a breakdown for food, energy and total excluding food and energy. Inflation measures the erosion of living standards

### Usage

```python wordwrap
ccpi [-c COUNTRIES] [-p {ENRG,FOOD,TOT,TOT_FOODENRG}] [--frequency {M,Q,A}] [-u {AGRWTH,IDX2015}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | What countries you'd like to collect data for | united_states | True | None |
| perspective | -p  --perspective | Perspective of CPI you wish to obtain. This can be ENRG (energy), FOOD (food), TOT (total) or TOT_FOODENRG (total excluding food and energy) | TOT | True | ENRG, FOOD, TOT, TOT_FOODENRG |
| frequency | --frequency | What frequency you'd like to collect data for | M | True | M, Q, A |
| units | -u  --units | Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015). Default is Annual Growth Rate (AGRWTH). | AGRWTH | True | AGRWTH, IDX2015 |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 2018-11-21 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | 2023-11-21 | True | None |

---
