---
title: hma
description: OpenBB Terminal Function
---

# hma

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
| n_offset | offset | 0 | True | range(0, 100) |

![hma](https://user-images.githubusercontent.com/46355364/154310988-2e97c166-a3b9-49ae-abcd-2c1b37309072.png)

---
