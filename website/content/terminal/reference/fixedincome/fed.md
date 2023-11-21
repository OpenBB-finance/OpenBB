---
title: fed
description: Get Effective Federal Funds Rate data
keywords:
- fixedincome
- fed
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /fed - Reference | OpenBB Terminal Docs" />

Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

### Usage

```python wordwrap
fed [-p {monthly,daily,weekly,daily_excl_weekend,annual,biweekly,volume}] [-s START_DATE] [-e END_DATE] [-o] [-q] [-t]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific Effective Federal Funds Rate data to retrieve | monthly | True | monthly, daily, weekly, daily_excl_weekend, annual, biweekly, volume |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1900-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |
| overnight | -o  --overnight | Gets the Overnight Bank Funding Rate | False | True | None |
| quantiles | -q  --quantiles | Whether to show 1, 25, 75 and 99 percentiles | False | True | None |
| target | -t  --target | Whether to show the target range data | False | True | None |

---
