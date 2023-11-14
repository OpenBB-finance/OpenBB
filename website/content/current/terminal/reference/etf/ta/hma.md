---
title: hma
description: Learn how to use the Hull Moving Average (HMA), a method that improves
  responsiveness to price activity and maintains curve smoothness. Understand how
  to use parameters like n_length and n_offset with the HMA.
keywords:
- Hull Moving Average
- moving average
- price activity
- curve smoothness
- lag elimination
- improved smoothing
- HMA usage
- n_length
- n_offset
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/hma - Reference | OpenBB Terminal Docs" />

The Hull Moving Average solves the age old dilemma of making a moving average more responsive to current price activity whilst maintaining curve smoothness. In fact the HMA almost eliminates lag altogether and manages to improve smoothing at the same time.

### Usage

```python
hma [-l N_LENGTH] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window lengths. Multiple values indicated as comma separated values. | 10, 20 | True | None |
| n_offset | offset | 0 | True | None |

![hma](https://user-images.githubusercontent.com/46355364/154310988-2e97c166-a3b9-49ae-abcd-2c1b37309072.png)

---
