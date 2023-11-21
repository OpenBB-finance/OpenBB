---
title: debt
description: General government debt-to-GDP ratio measures the gross debt of the general government as a percentage of GDP
keywords:
- economy
- debt
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /debt - Reference | OpenBB Terminal Docs" />

General government debt-to-GDP ratio measures the gross debt of the general government as a percentage of GDP. It is a key indicator for the sustainability of government finance.

### Usage

```python wordwrap
debt [-c COUNTRIES] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 1993-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2023-11-21 | True | None |

---
