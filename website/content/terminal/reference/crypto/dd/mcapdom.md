---
title: mcapdom
description: The mcapdom documentation page presents an outline of how to display
  an asset's percentage share of the total crypto circulating market cap. It includes
  usage and parameters specifically for frequency interval, initial date, and end
  date.
keywords:
- mcapdom
- crypto circulating market cap
- asset's percentage share
- frequency interval
- initial date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /dd/mcapdom - Reference | OpenBB Terminal Docs" />

Display asset's percentage share of total crypto circulating market cap [Source: https://messari.io]

### Usage

```python wordwrap
mcapdom [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| interval | -i  --interval | Frequency interval. Default: 1d | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | -s  --start | Initial date. Default: A year ago | 2022-11-21 | True | None |
| end | -end  --end | End date. Default: Today | 2023-11-21 | True | None |

---
