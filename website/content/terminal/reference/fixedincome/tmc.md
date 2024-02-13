---
title: tmc
description: Get 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data
keywords:
- fixedincome
- tmc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /tmc - Reference | OpenBB Terminal Docs" />

Get 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data. Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

### Usage

```python wordwrap
tmc [-p {3_month,2_year}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Selected treasury constant maturity to subtract | 3_month | True | 3_month, 2_year |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
