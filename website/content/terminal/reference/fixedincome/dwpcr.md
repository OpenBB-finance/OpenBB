---
title: dwpcr
description: Get Discount Window Primary Credit Rate data
keywords:
- fixedincome
- dwpcr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /dwpcr - Reference | OpenBB Terminal Docs" />

Get Discount Window Primary Credit Rate data. A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

### Usage

```python wordwrap
dwpcr [-p {daily_excl_weekend,monthly,weekly,daily,annual}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific Discount Window Primary Credit Rate data to retrieve | daily_excl_weekend | True | daily_excl_weekend, monthly, weekly, daily, annual |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
