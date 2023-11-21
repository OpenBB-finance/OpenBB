---
title: balance
description: General government balance is defined as the balance of income and expenditure of government, including capital income and capital expenditures
keywords:
- economy
- balance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /balance - Reference | OpenBB Terminal Docs" />

General government balance is defined as the balance of income and expenditure of government, including capital income and capital expenditures. 'Net lending' means that government has a surplus, and is providing financial resources to other sectors, while 'net borrowing' means that government has a deficit, and requires financial resources from other sectors. This indicator is measured as a percentage of GDP.

### Usage

```python wordwrap
balance [-c COUNTRIES] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 1993-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
