---
title: spending
description: General government spending provides an indication of the size of government across countries
keywords:
- economy
- spending
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /spending - Reference | OpenBB Terminal Docs" />

General government spending provides an indication of the size of government across countries. The large variation in this indicator highlights the variety of countries' approaches to delivering public goods and services and providing social protection, not necessarily differences in resources spent

### Usage

```python wordwrap
spending [-c COUNTRIES] [-p {TOT,RECULTREL,HOUCOMM,PUBORD,EDU,ENVPROT,GRALPUBSER,SOCPROT,ECOAFF,DEF,HEALTH}] [-u {PC_GDP,THND_USD_CAP}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| perspective | -p  --perspective | Use either TOT (Total), RECULTREL (Recreation, culture and religion), HOUCOMM (Housing and community amenities), PUBORD (Public order and safety), EDU (Education), ENVPROT (Environmental protection), GRALPUBSER (General public services), SOCPROT (Social protection), ECOAFF (Economic affairs), DEF (Defence), HEALTH (Health) | TOT | True | TOT, RECULTREL, HOUCOMM, PUBORD, EDU, ENVPROT, GRALPUBSER, SOCPROT, ECOAFF, DEF, HEALTH |
| units | -u  --units | Use either THND_USD_CAP (thousands of USD per capity) or PC_GDP (percentage of GDP) | PC_GDP | True | PC_GDP, THND_USD_CAP |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 1993-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
