---
title: calc
description: OpenBB Terminal Function
---

# calc

Calculate profit or loss for given option settings.

### Usage

```python
calc [--put] [--sell] [-s STRIKE] [-p PREMIUM] [-m MIN] [-M MAX]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| put | Flag to calculate put option | False | True | None |
| sell | Flag to get profit chart of selling contract | False | True | None |
| strike | Option strike price | 10 | True | None |
| premium | Premium price | 1 | True | None |
| min | Min price to look at | -1 | True | None |
| max | Max price to look at | -1 | True | None |


---

## Examples

```python
2022 Feb 16, 08:45 (🦋) /stocks/options/ $ calc -s 30 -p 6 -m 1 -M 50

Strike: $30.0
Premium: $6.0
Breakeven price: $36.0
Max profit: Unlimited
Max loss: $-600.0
```
![calc](https://user-images.githubusercontent.com/46355364/154277755-a6640bee-8621-4a7d-9fc6-9c197daca0e1.png)

---
