---
title: closetrade
description: Documentation for the command 'closetrade', which allows for closing
  trades by ID. It enables specification of the number of units to close, with relevant
  parameters detailed.
keywords:
- closetrade
- trade
- orderID
- units
- close trade
- parameters
- trade ID
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/oanda/closetrade - Reference | OpenBB Terminal Docs" />

Close a trade by id.

### Usage

```python
closetrade [-i ORDERID] [-u UNITS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| orderID | The Trade ID to close. | None | True | None |
| units | The number of units on the trade to close. If not set it defaults to all units. | None | True | None |

---
