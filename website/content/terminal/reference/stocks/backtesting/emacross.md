---
title: emacross
description: OpenBB Terminal Function
---

# emacross

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
