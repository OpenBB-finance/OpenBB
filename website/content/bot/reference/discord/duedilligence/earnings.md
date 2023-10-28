---
title: earnings
description: Details on how to use the 'earnings' command to retrieve anticipated
  earnings for a specified business day. Information includes company ticker, expected
  time, sector, and float facilitating informed investment decisions.
keywords:
- earnings
- investment decisions
- company ticker
- business day
- sector
- float
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: earnings - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the expected earnings for the given business day. The displayed earnings will include company ticker, expected time, sector, and float of the company. This information can be used to help the user make informed decisions about their investments.

### Usage

```python wordwrap
/dd earnings day
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| day | Date to get earnings for (YYYY-MM-DD) | False | None |


---

## Examples

```
/dd earnings day:2022-07-29
```
---
