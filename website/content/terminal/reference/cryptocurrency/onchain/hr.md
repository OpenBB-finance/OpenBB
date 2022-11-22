---
title: hr
description: OpenBB Terminal Function
---

# hr

Display mean hashrate for a certain blockchain (ETH or BTC) [Source: https://glassnode.org]

### Usage

```python
usage: hr [-c {BTC,ETH}] [-i {24h,1w,1month}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| coin | Coin to check hashrate (BTC or ETH) | BTC | True | BTC, ETH |
| interval | Frequency interval. Default: 24h | 24h | True | 24h, 1w, 1month |
| since | Initial date. Default: 2021-11-22 | 2021-11-22 | True | None |
| until | Final date. Default: 2022-11-22 | 2022-11-22 | True | None |
---

