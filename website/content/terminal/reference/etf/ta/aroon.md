---
title: aroon
description: This page provides a comprehensive detail on 'Aroon' - an indicator that
  shows when a new trend is dawning in the market. It explains how to interpret upward
  and downward trends as well as crossovers.
keywords:
- aroon
- marketing
- trend
- indicator
- upward trend
- downward trend
- crossovers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/aroon - Reference | OpenBB Terminal Docs" />

The word aroon is Sanskrit for "dawn's early light." The Aroon indicator attempts to show when a new trend is dawning. The indicator consists of two lines (Up and Down) that measure how long it has been since the highest high/lowest low has occurred within an n period range. When the Aroon Up is staying between 70 and 100 then it indicates an upward trend. When the Aroon Down is staying between 70 and 100 then it indicates an downward trend. A strong upward trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30. Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above the Aroon Up, it indicates a weakening of the upward trend (and vice versa).

### Usage

```python
aroon [-l N_LENGTH] [-s N_SCALAR]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 25 | True | None |
| n_scalar | scalar | 100 | True | None |

![aroon](https://user-images.githubusercontent.com/46355364/154309825-f8ccc98b-31ac-43fc-a251-66f6f41545a5.png)

---
