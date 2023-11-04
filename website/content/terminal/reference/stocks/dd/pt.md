---
title: pt
description: The pt command can print the latest price targets from analysts as provided
  by Business Insider. The command has parameters such as raw for displaying only
  raw data, and limit for controlling the number of price targets shown.
keywords:
- Business Insider
- Price Target
- Analysts
- Parameters
- Raw data
- Limit
- Latest price targets
- Print
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/dd/pt - Reference | OpenBB Terminal Docs" />

Prints price target from analysts. [Source: Business Insider]

### Usage

```python
pt [--raw] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| raw | Only output raw data | False | True | None |
| limit | Limit of latest price targets from analysts to print. | 10 | True | None |

![pt](https://user-images.githubusercontent.com/46355364/154235470-58ed232e-116e-442a-bffe-8e855eba3bda.png)

---
