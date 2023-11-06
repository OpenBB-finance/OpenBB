---
title: sectorsflow
description: The sectorsflow command page details how to retrieve a summary of all
  flows by MarketCap percentage per sector over past specified days. It includes nuances
  on usage and different parameters like sector and number of days.
keywords:
- sectorsflow
- MarketCap percentage
- sector
- days
- flow summary
- Basic Materials
- Energy
- Communication Services
- Consumer Cyclical
- Consumer Defensive
- Financial
- Healthcare
- Industrials
- Real Estate
- Technology
- Utilities
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: sectorsflow - Telegram Reference | OpenBB Bot Docs" />

This command retrieves a summary of all flows by MarketCap percentage per sector over the past x days.

### Usage

```python wordwrap
/sectorsflow days sector
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sector | Sector to filter by: `bm` (Basic Materials), `e` (Energy), `cs` (Communication Services), `cc` (Consumer Cyclical), `cd` (Consumer Defensive), `f` (Financial), `h` (Healthcare), `i` (Industrials), `re` (Real Estate), `t` (Technology), `u` (Utilities) | False | None |


---

## Examples

```
/sectorsflow 5 cs
```

```
/sectorsflow 5 bm
```
---
