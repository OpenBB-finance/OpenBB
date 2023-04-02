---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sectors
description: OpenBB Discord Command
---

# sectors

This command allows the user to retrieve a summary of all prints by % of MarketCap by Sector over the last 5 days, with a focus on Basic Materials sector. The user will be able to view the basic materials sector's market cap over the last 5 days, as well as the overall market cap of all sectors over the last 5 days.

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
