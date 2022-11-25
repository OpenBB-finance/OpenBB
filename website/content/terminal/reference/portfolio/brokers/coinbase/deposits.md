---
title: deposits
description: OpenBB Terminal Function
---

# deposits

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
