---
title: emacross
description: The emacross page provides documentation for a python script that crosses
  between a long and a short Exponential Moving Average (EMA). It also includes information
  on the parameters of the script including lengths of the long and short EMA periods,
  spy hold comparison, buy hold comparison, and short selling operations.
keywords:
- emacross
- Exponential Moving Average
- EMA period
- long EMA
- short EMA
- spy hold comparison
- buy hold comparison
- short sell
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/backtesting/emacross - Reference | OpenBB Terminal Docs" />

Cross between a long and a short Exponential Moving Average.

### Usage

```python
emacross [-l LONG] [-s SHORT] [--spy] [--no_bench] [--no_short]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| long | Long EMA period | 50 | True | None |
| short | Short EMA period | 20 | True | None |
| spy | Flag to add spy hold comparison | False | True | None |
| no_bench | Flag to not show buy and hold comparison | False | True | None |
| shortable | Flag that disables the short sell | True | True | None |

---
