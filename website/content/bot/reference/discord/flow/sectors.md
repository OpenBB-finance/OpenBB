---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sectors
description: OpenBB Discord Command
---

# sectors

This command retrieves a summary of all flows by MarketCap percentage by sector over the past 5 days, with a focus on energy sector. It provides an overview of the total flow, the composition of the flow, and the recent price and returns for the sector.

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
