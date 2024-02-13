---
title: sonia
description: SONIA (Sterling Overnight Index Average) is an important interest rate benchmark
keywords:
- fixedincome
- sonia
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /sonia - Reference | OpenBB Terminal Docs" />

SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other financial institutions and other institutional investors.

### Usage

```python wordwrap
sonia [-p {rate,index,10th_percentile,25th_percentile,75th_percentile,90th_percentile,total_nominal_value}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific SONIA data to retrieve | rate | True | rate, index, 10th_percentile, 25th_percentile, 75th_percentile, 90th_percentile, total_nominal_value |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
