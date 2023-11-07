---
title: contracts
description: This documentation page provides information about contracts associated
  with a ticker as sourced from QuiverQuant. Details include usage, parameters like
  past transaction days and raw data. Also added is a snapshot of the contracts interface.
keywords:
- contracts
- past transaction days
- raw data
- quiverquant
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/gov/contracts - Reference | OpenBB Terminal Docs" />

Contracts associated with ticker. [Source: www.quiverquant.com]

### Usage

```python
contracts [-p PAST_TRANSACTION_DAYS] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| past_transaction_days | Past transaction days | 10 | True | None |
| raw | Print raw data. | False | True | None |

![contracts](https://user-images.githubusercontent.com/46355364/154263066-0ff61349-4fe5-4eac-9e60-23fa075a9e9f.png)

---
