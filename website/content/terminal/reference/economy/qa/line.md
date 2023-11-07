---
title: line
description: The page provides a detailed overview on how to use the 'line' function
  in Python to visualize data on a line plot. It provides parameters for customizing
  the plot such as scale, markers and highlighting specific events.
keywords:
- line plot
- data visualization
- log scale
- line markers
- scatter markers
- highlight events
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/qa/line - Reference | OpenBB Terminal Docs" />

Show line plot of selected data or highlight specific datetimes.

### Usage

```python
line [--log] [--ml ML] [--ms MS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| log | Plot with y on log scale | False | True | None |
| ml | Draw vertical line markers to highlight certain events |  | True | None |
| ms | Draw scatter markers to highlight certain events |  | True | None |

![line](https://user-images.githubusercontent.com/46355364/154307397-9c2e9325-bce6-494d-994f-a6d7db798798.png)

---
