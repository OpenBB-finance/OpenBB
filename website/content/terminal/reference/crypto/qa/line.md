---
title: line
description: This page is a comprehensive guide on how to create line plots of selected
  data, and how to highlight specific datetimes. It provides information about different
  parameters like log scale plotting, vertical line markers, and scatter markers.
keywords:
- line plot
- data visualization
- datetime highlighting
- log scale plotting
- vertical line markers
- scatter markers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/line - Reference | OpenBB Terminal Docs" />

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
| ml | Draw vertical line markers to highlight certain events (comma separated dates, e.g. 2020-01-01,2020-02-01) |  | True | None |
| ms | Draw scatter markers to highlight certain events (comma separated dates, e.g. 2021-01-01,2021-02-01) |  | True | None |

![line](https://user-images.githubusercontent.com/46355364/154307397-9c2e9325-bce6-494d-994f-a6d7db798798.png)

---
