---
title: vol
description: The 'vol' page provides command-line instructions for plotting volumes.
  It deals with parameters like minimal and maximal strikes, calls, and puts. The
  page is mainly focused on contracts traded today and the plotting of call or put
  options only.
keywords:
- vol
- volume
- contracts traded
- plot volume
- min strike
- max strike
- calls
- puts
- options
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/vol - Reference | OpenBB Terminal Docs" />

Plot volume. Volume refers to the number of contracts traded today.

### Usage

```python
vol [-m MIN] [-M MAX] [-c] [-p]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| min | Min strike to plot | -1 | True | None |
| max | Max strike to plot | -1 | True | None |
| calls | Flag to plot call options only | False | True | None |
| puts | Flag to plot put options only | False | True | None |

![vol](https://user-images.githubusercontent.com/46355364/154291303-c23edf53-4242-4d9b-a45e-22ce8a633aa8.png)

---
