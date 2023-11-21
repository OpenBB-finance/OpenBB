---
title: rgdp
description: This indicator is based on real GDP (also called GDP at constant prices or GDP in volume), i
keywords:
- economy
- rgdp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /rgdp - Reference | OpenBB Terminal Docs" />

This indicator is based on real GDP (also called GDP at constant prices or GDP in volume), i.e. the developments over time are adjusted for price changes.

### Usage

```python wordwrap
rgdp [-c COUNTRIES] [-u {PC_CHGPP,PC_CHGPY,IDX}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| units | -u  --units | Use either PC_CHGPP (percentage change previous quarter), PC_CHGPY (percentage change from the same quarter of the previous year) or IDX (index with base at 2015) for units | PC_CHGPY | True | PC_CHGPP, PC_CHGPY, IDX |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 2013-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
