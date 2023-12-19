---
title: acf
description: The page provides explanation and usage for acf- the Auto-Correlation
  and Partial Auto-Correlation Functions for diff and diff diff crypto data. It includes
  parameters details and illustrative plot.
keywords:
- acf
- Auto-Correlation
- Partial Auto-Correlation
- diff
- diff diff
- crypto data
- lags
- plots
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/acf - Reference | OpenBB Terminal Docs" />

Auto-Correlation and Partial Auto-Correlation Functions for diff and diff diff crypto data

### Usage

```python
acf [-l LAGS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| lags | maximum lags to display in plots | 15 | True | range(5, 100) |

![acf](https://user-images.githubusercontent.com/46355364/154305242-176c3ba1-ebfc-43e7-a027-46251fb02463.png)

---
