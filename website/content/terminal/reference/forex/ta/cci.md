---
title: cci
description: A detailed guide on the CCI or Commodity Channel Index, its usage, parameters
  and its role in detecting market trends and facilitating price correction.
keywords:
- CCI
- Commodity Channel Index
- CCI usage
- market trends
- price correction
- overbought conditions
- oversold conditions
- CCI parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/ta/cci - Reference | OpenBB Terminal Docs" />

The CCI is designed to detect beginning and ending market trends. The range of 100 to -100 is the normal trading range. CCI values outside of this range indicate overbought or oversold conditions. You can also look for price divergence in the CCI. If the price is making new highs, and the CCI is not, then a price correction is likely.

### Usage

```python
cci [-l N_LENGTH] [-s N_SCALAR]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | None |
| n_scalar | scalar | 0.015 | True | None |

![cci](https://user-images.githubusercontent.com/46355364/154310079-808803ca-26dd-4d45-8a02-17e51230bf2d.png)

---
