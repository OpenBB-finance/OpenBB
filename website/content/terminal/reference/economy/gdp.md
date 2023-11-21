---
title: gdp
description: This indicator is based on nominal GDP (also called GDP at current prices or GDP in value) and is available in different measures US dollars and US dollars per capita (current PPPs)
keywords:
- economy
- gdp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /gdp - Reference | OpenBB Terminal Docs" />

This indicator is based on nominal GDP (also called GDP at current prices or GDP in value) and is available in different measures: US dollars and US dollars per capita (current PPPs).

### Usage

```python wordwrap
gdp [-c COUNTRIES] [-u {USD,USD_CAP}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| units | -u  --units | Use either USD or USD_CAP (USD Per Capita) | USD | True | USD, USD_CAP |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 1993-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
