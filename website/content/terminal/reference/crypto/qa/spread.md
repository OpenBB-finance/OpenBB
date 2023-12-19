---
title: spread
description: This page illustrates the rolling spread measurement, its usage, and
  the parameters involved in it. It comprehensively explains how to use 'spread' and
  the function of 'n_window' in it.
keywords:
- spread measurement
- usage of spread
- spread parameters
- n_window in spread
- rolling spread
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/spread - Reference | OpenBB Terminal Docs" />

Shows rolling spread measurement

### Usage

```python
spread [-w N_WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | Window length | 14 | True | range(5, 100) |

![spread](https://user-images.githubusercontent.com/46355364/154308406-f20812a4-fa04-4937-b8de-dc27042f7462.png)

---
