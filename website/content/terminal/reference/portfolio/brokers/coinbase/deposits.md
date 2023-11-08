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

<HeadTitle title="portfolio/coinbase/deposits /brokers - Reference | OpenBB Terminal Docs" />

Display a list of deposits for your account.

### Usage

```python
deposits [-t {internal_deposit,deposit}] [-l LIMIT] [-s {created_at,amount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| type | Deposit type. Either: internal_deposits (transfer between portfolios) or deposit | deposit | True | internal_deposit, deposit |
| limit | Limit parameter. | 20 | True | None |
| sortby | Sort by given column. Default: created_at | created_at | True | created_at, amount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
