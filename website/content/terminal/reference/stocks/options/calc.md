---
title: calc
description: OpenBB Terminal Function
---

# calc

Calculate profit or loss for given option settings.

### Usage

```python
usage: calc [--put] [--sell] [-s STRIKE] [-p PREMIUM] [-m MIN] [-M MAX]
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

