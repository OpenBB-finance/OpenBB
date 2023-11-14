---
title: psi
description: The page provides detailed information about psi command which shows
  the price vs short interest volume data from either NYSE or NASDAQ taken from Quandl
  or Stockgrid. It also includes usage and parameter details.
keywords:
- psi
- NYSE
- NASDAQ
- Quandl
- Stockgrid
- short-interest volume
- price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/dps/psi - Reference | OpenBB Terminal Docs" />

Shows price vs short interest volume. [Source: Quandl/Stockgrid]

### Usage

```python
psi [--nyse]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_nyse | Data from NYSE flag. Otherwise comes from NASDAQ. Only works for Quandl. | False | True | None |

![Figure_2](https://user-images.githubusercontent.com/46355364/154076731-e1f5ad9c-71c7-4c56-93b1-613985057951.png)

---
