---
title: revenue
description: Governments collect revenues mainly for two purposes to finance the goods and services they provide to citizens and businesses, and to fulfil their redistributive role
keywords:
- economy
- revenue
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /revenue - Reference | OpenBB Terminal Docs" />

Governments collect revenues mainly for two purposes: to finance the goods and services they provide to citizens and businesses, and to fulfil their redistributive role. Comparing levels of government revenues across countries provides an indication of the importance of the government sector in the economy in terms of available financial resources.

### Usage

```python wordwrap
revenue [-c COUNTRIES] [-u {PC_GDP,THND_USD_CAP}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| units | -u  --units | Use either THND_USD_CAP (thousands of USD per capity) or PC_GDP (percentage of GDP) | PC_GDP | True | PC_GDP, THND_USD_CAP |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 1993-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
