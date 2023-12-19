---
title: aprtoapy
description: APR to APY conversion tool. Use aprtoapy tool to compute APY value from
  APR, defining the number of compounding periods per year.
keywords:
- aprtoapy
- APR
- APY
- compounding
- finance tools
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/tools/aprtoapy - Reference | OpenBB Terminal Docs" />

Tool to calculate APY from APR value. Compouding periods, i.e., the number of times compounded per year can be defined with -c argument.

### Usage

```python
aprtoapy [--apr APR] [-c COMPOUNDING] [-n]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| apr | APR value in percentage to convert | 100 | True | range(1, 101) |
| compounding | Number of compounded periods in a year. 12 means compounding monthly | 12 | True | range(1, 101) |
| narrative | Flag to show narrative instead of dataframe | False | True | None |

---
