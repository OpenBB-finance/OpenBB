---
title: deposits
description: The deposits page is a comprehensive guide on displaying a list of deposits
  for your account. It provides details on usage, parameters like deposit type, limit,
  sortby, reverse, and their defaults.
keywords:
- deposits
- account
- internal_deposit
- deposit
- limit
- sortby
- reverse
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /brokers/coinbase/deposits - Reference | OpenBB Terminal Docs" />

Display a list of deposits for your account.

### Usage

```python wordwrap
deposits [-t {internal_deposit,deposit}] [-l LIMIT] [-s {created_at,amount}] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| type | -t  --type | Deposit type. Either: internal_deposits (transfer between portfolios) or deposit | deposit | True | internal_deposit, deposit |
| limit | -l  --limit | Limit parameter. | 20 | True | None |
| sortby | -s  --sort | Sort by given column. Default: created_at | created_at | True | created_at, amount |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
