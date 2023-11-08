---
title: heatmap
description: This page describes how to use the heatmap tool which provides an interactive
  treemap of the SP 500 from finviz. It includes usage examples and a detailed description
  of parameters.
keywords:
- heatmap tool
- SP 500 heatmap
- interactive treemap
- finviz
- usage examples
- tool parameters
- timeframe parameter
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/disc/heatmap - Reference | OpenBB Terminal Docs" />

Get the SP 500 heatmap from finviz and display in interactive treemap

### Usage

```python
heatmap [-t {day,week,month,3month,6month,year,ytd}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| timeframe | Timeframe to get heatmap data for | day | True | day, week, month, 3month, 6month, year, ytd |

---
