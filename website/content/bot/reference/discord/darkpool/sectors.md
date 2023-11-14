---
title: sectors
description: The page provides information on how to use the sectors command, which
  allows the user to view a summary of all prints by MarketCap of different sectors
  over a given period. The command provides significant insights into the darkpool
  activities of different sectors.
keywords:
- sectors command
- MarketCap by Sector
- darkpool activity
- sector's market cap
- accumulation
- Basic Materials
- Energy sector
- Communication Services
- Consumer Cyclical
- Consumer Defensive
- Financial sector
- Healthcare sector
- Industrials
- Real Estate sector
- Technology sector
- Utilities sector
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: sectors - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a summary of all prints by % of MarketCap by Sector over the last x days. The user will be able to view the sector's market cap divided by total darkpool activity to see possible accumulation.

### Usage

```python wordwrap
/dp sectors days sector
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sector | Sector to filter by | False | Basic Materials (BM), Energy (E), Communication Services (CS), Consumer Cyclical (CC), Consumer Defensive (CD), Financial (F), Healthcare (H), Industrials (I), Real Estate (RE), Technology (T), Utilities (U) |


---

## Examples

```
/dp sectors days:5 sector:Basic Materials
```

---
