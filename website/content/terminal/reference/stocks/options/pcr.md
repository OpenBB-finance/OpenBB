---
title: pcr
description: This marketing webpage demonstrates the usage of the 'pcr' function that
  displays put to call ratio for a particular ticker. It includes a detailed parameters'
  list and a plot for visualization.
keywords:
- Put Call Ratio
- AlphaQuery
- pcr function
- visualization
- parameters description
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/pcr - Reference | OpenBB Terminal Docs" />

Display put to call ratio for ticker [AlphaQuery.com]

### Usage

```python
pcr [-l {10,20,30,60,90,120,150,180}] [-s START]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| length | Window length to get | 30 | True | 10, 20, 30, 60, 90, 120, 150, 180 |
| start | Start date for plot | datetime.now() - timedelta(days=365) | True | None |

![pcr](https://user-images.githubusercontent.com/46355364/154286299-19ea423d-28e7-48d7-a5f3-621f0428fd4a.png)

---
