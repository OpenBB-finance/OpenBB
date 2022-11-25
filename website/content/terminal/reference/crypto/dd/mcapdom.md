---
title: mcapdom
description: OpenBB Terminal Function
---

# mcapdom

Display asset's percentage share of total crypto circulating market cap [Source: https://messari.io]

### Usage

```python
mcapdom [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| interval | Frequency interval. Default: 1d | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |

---
