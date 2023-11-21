---
title: spot
description: The spot rate for any maturity is the yield on a bond that provides a single payment at that maturity
keywords:
- fixedincome
- spot
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /spot - Reference | OpenBB Terminal Docs" />

The spot rate for any maturity is the yield on a bond that provides a single payment at that maturity. This is a zero coupon bond. Because each spot rate pertains to a single cashflow, it is the relevant interest rate concept for discounting a pension liability at the same maturity.

### Usage

```python wordwrap
spot [-m MATURITY] [-c CATEGORY] [-d] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| maturity | -m  --maturity | What maturity you'd like to collect data for | 10y | True | None |
| category | -c  --category | What category you'd like to collect data for | spot_rate | True | None |
| description | -d  --description | Whether to provide a description of the data. | False | True | None |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
