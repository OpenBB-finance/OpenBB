---
title: usrates
description: Plot various rates from the United States
keywords:
- fixedincome
- usrates
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /usrates - Reference | OpenBB Terminal Docs" />

Plot various rates from the United States. This includes tbill (Treasury Bills), Constant Maturity treasuries (cmn) and Inflation Protected Treasuries (TIPS)

### Usage

```python wordwrap
usrates [-m {4_week,1_month,3_month,6_month,1_year,2_year,3_year,5_year,7_year,10_year,20_year,30_year}] [-p {tbill,cmn,tips}] [-o] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| maturity | -m  --maturity | Specific Treasury Bill Secondary Market Rate data to plot | 3_month | True | 4_week, 1_month, 3_month, 6_month, 1_year, 2_year, 3_year, 5_year, 7_year, 10_year, 20_year, 30_year |
| parameter | -p  --parameter | Choose either tbill (Treasury Bills), Constant Maturity treasuries (cmn) or Inflation Protected Treasuries (TIPS) | tbill | True | tbill, cmn, tips |
| options | -o  --options | See the available options | False | True | None |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
