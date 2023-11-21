---
title: ffrmc
description: Get Selected Treasury Constant Maturity Minus Federal Funds Rate
keywords:
- fixedincome
- ffrmc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /ffrmc - Reference | OpenBB Terminal Docs" />

Get Selected Treasury Constant Maturity Minus Federal Funds Rate. Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

### Usage

```python wordwrap
ffrmc [-p {10_year,5_year,1_year,6_month,3_month}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Selected Treasury Constant Maturity | 10_year | True | 10_year, 5_year, 1_year, 6_month, 3_month |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
