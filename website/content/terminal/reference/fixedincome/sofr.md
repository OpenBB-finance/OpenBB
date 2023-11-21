---
title: sofr
description: The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of borrowing cash overnight collateralized by Treasury securities
keywords:
- fixedincome
- sofr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /sofr - Reference | OpenBB Terminal Docs" />

The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of borrowing cash overnight collateralized by Treasury securities. The SOFR is calculated as a volume-weighted median of transaction-level tri-party repo data.

### Usage

```python wordwrap
sofr [-p {overnight,30_day_average,90_day_average,180_day_average,index}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific SOFR data to retrieve | overnight | True | overnight, 30_day_average, 90_day_average, 180_day_average, index |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
