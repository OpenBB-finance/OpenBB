---
title: cp
description: Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations
keywords:
- fixedincome
- cp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /cp - Reference | OpenBB Terminal Docs" />

Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations. Maturities range up to 270 days but average about 30 days. Many companies use CP to raise cash needed for current transactions, and many find it to be a lower-cost alternative to bank loans.

### Usage

```python wordwrap
cp [-m {15d,30d,60d,7d,90d,overnight}] [-c {asset_backed,financial,non_financial,spread}] [-g {a2_p2,aa}] [-o] [-d] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| maturity | -m  --maturity | What type you'd like to collect data for | 30d | True | 15d, 30d, 60d, 7d, 90d, overnight |
| category | -c  --category | What category you'd like to collect data for | financial | True | asset_backed, financial, non_financial, spread |
| grade | -g  --grade | What grade you'd like to collect data for | aa | True | a2_p2, aa |
| options | -o  --options | See the available options | False | True | None |
| description | -d  --description | Whether to provide a description of the data. | False | True | None |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
