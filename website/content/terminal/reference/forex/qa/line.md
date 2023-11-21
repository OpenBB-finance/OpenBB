---
title: line
description: The 'line' documentation page provides information on how to create a
  line plot of selected data or highlight specific datetimes. It also details the
  usage, parameters, and provides a visual representation.
keywords:
- line plot
- highlight specific datetimes
- log scale plotting
- vertical line markers
- scatter markers
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/line - Reference | OpenBB Terminal Docs" />

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
