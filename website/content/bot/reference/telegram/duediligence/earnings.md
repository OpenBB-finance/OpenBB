---
title: earnings
description: This command allows the user to retrieve the expected earnings for a
  given business day including company ticker, and other details. This information
  aids in making informed decisions about their investments.
keywords:
- expected earnings
- business day
- company ticker
- investment decisions
- parameters
- investment examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duediligence: earnings - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the expected earnings for the given business day. The displayed earnings will include company ticker, expected time, sector, and float of the company. This information can be used to help the user make informed decisions about their investments.

### Usage

```python wordwrap
/earnings day
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| day | Date to get earnings for (YYYY-MM-DD) | False | None |


---

## Examples

```
/earnings 2022-07-29
```

---
