---
title: active
description: This page provides information on how to display active blockchain addresses
  over time including usage, parameters and visualization. The data source is Glassnode.
keywords:
- Blockchain
- Addresses
- Active
- Glassnode
- Data visualization
- Frequency Interval
- Initial Date
- Final Date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/active - Reference | OpenBB Terminal Docs" />

Display active blockchain addresses over time [Source: https://glassnode.org]

### Usage

```python
active [-i {24h,1w,1month}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| interval | Frequency interval. Default: 24h | 24h | True | 24h, 1w, 1month |
| since | Initial date. Default: 1 year ago | 2021-11-25 | True | None |
| until | Final date. Default: Today | 2022-11-25 | True | None |

![active](https://user-images.githubusercontent.com/46355364/154058739-e30fed47-c86f-4aef-a699-1bc69180c607.png)

---
