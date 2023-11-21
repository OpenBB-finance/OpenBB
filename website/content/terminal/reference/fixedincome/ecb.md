---
title: ecb
description: Plot the three interest rates the ECB sets every six weeks as part of its monetary policy, these are the interest rate on the main refinancing operations (MRO), the rate on the deposit facility and the rate on the marginal lending facility
keywords:
- fixedincome
- ecb
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /ecb - Reference | OpenBB Terminal Docs" />

Plot the three interest rates the ECB sets every six weeks as part of its monetary policy, these are the interest rate on the main refinancing operations (MRO), the rate on the deposit facility and the rate on the marginal lending facility.

### Usage

```python wordwrap
ecb [-s START_DATE] [-e END_DATE] [-t {deposit,lending,refinancing}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |
| type | -t  --type | Whether to choose the deposit, marginal lending or main refinancing rate | None | True | deposit, lending, refinancing |

---
