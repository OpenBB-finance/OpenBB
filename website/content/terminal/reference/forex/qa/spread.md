---
title: spread
description: A documentation page detailing how to use the spread measurement tool.
  The page includes parameters, usage, and visuals to guide the user.
keywords:
- spread measurement
- rolling spread
- usage
- parameters
- n_window
- window length
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/spread - Reference | OpenBB Terminal Docs" />

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
