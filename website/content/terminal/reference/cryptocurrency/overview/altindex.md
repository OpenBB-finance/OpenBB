---
title: altindex
description: OpenBB Terminal Function
---

# altindex

Display altcoin index overtime. If 75% of the Top 50 coins performed better than Bitcoin over periods of time (30, 90 or 365 days) it is Altcoin Season. Excluded from the Top 50 are Stablecoins (Tether, DAI…) and asset backed tokens (WBTC, stETH, cLINK,…) [Source: https://blockchaincenter.net]

### Usage

```python
usage: altindex [-p {30,90,365}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period of time to check if how altcoins have performed against btc (30, 90, 365) | 365 | True | 30, 90, 365 |
| since | Start date (default: 1 year before, e.g., 2021-01-01) | 2021-11-22 | True | None |
| until | Final date. Default is current date | 2022-11-22 | True | None |
---

