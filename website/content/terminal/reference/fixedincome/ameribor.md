---
title: ameribor
description: Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of short-term interbank borrowing
keywords:
- fixedincome
- ameribor
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /ameribor - Reference | OpenBB Terminal Docs" />

Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the American Financial Exchange (AFX).

### Usage

```python wordwrap
ameribor [-p {overnight,term_30,term_90,1_week_term_structure,1_month_term_structure,3_month_term_structure,6_month_term_structure,1_year_term_structure,2_year_term_structure,30_day_ma,90_day_ma}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific AMERIBOR data to retrieve | overnight | True | overnight, term_30, term_90, 1_week_term_structure, 1_month_term_structure, 3_month_term_structure, 6_month_term_structure, 1_year_term_structure, 2_year_term_structure, 30_day_ma, 90_day_ma |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
