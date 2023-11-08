---
title: map
description: The documentation outlines the usage and parameters of a performance
  index stocks map placed according to sectors and industries. The Web-Based map tool,
  sourced by Finviz, adjusts based on selected performance periods and map filter
  types, such as SP500, world, full or ETF.
keywords:
- Performance index
- stocks map
- sectors and industries
- market cap
- Finviz
- map filter type
- Performance period
- sp500
- world
- full
- etf
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /map - Reference | OpenBB Terminal Docs" />

Performance index stocks map categorized by sectors and industries. Size represents market cap. Opens web-browser. [Source: Finviz]

### Usage

```python
map [-p {1d,1w,1m,3m,6m,1y}] [-t {sp500,world,full,etf}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| s_period | Performance period. | 1d | True | 1d, 1w, 1m, 3m, 6m, 1y |
| s_type | Map filter type. | sp500 | True | sp500, world, full, etf |

![map](https://user-images.githubusercontent.com/46355364/154042399-ede7eb15-de7f-4de7-8541-3700ad2a97a0.png)

---
