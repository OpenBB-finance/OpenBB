---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sectors
description: OpenBB Discord Command
---

# sectors

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
