---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sectorsflow
description: OpenBB Telegram Command
---

# sectorsflow

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
