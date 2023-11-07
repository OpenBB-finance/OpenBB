---
title: sectors
description: This page provides guidelines for using the 'sectors' command to retrieve
  a summary of all flows by MarketCap percentage per sector over the specified number
  of past days. The command allows you to filter by selected sectors such as Basic
  Materials, Energy and Communication Services among others.
keywords:
- sectors
- flows
- MarketCap
- filtering
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

<HeadTitle title="flow: sectors - Discord Reference | OpenBB Bot Docs" />

This command retrieves a summary of all flows by MarketCap percentage per sector over the past x days.

### Usage

```python wordwrap
/flow sectors days sector
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
/flow sectors days:5 sector:Energy
```

```
/flow sectors days:2 sector:Communication Services
```

---
