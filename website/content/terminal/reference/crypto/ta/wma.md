---
title: wma
description: OpenBB Terminal Function
---

# wma

A Weighted Moving Average puts more weight on recent data and less on past data. This is done by multiplying each bar’s price by a weighting factor. Because of its unique calculation, WMA will follow prices more closely than a corresponding Simple Moving Average.

### Usage

```python
wma [-l N_LENGTH] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window lengths. Multiple values indicated as comma separated values. | 20, 50 | True | None |
| n_offset | offset | 0 | True | range(0, 100) |

![wma](https://user-images.githubusercontent.com/46355364/154312618-43430406-97c1-4740-87be-2414de9a1c06.png)

---
