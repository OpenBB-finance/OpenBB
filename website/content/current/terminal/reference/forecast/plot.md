---
title: plot
description: This page provides an elaborative guide to users on how to plot data
  based on their index with interactive examples.
keywords:
- Data Plotting
- Plot usage
- Dataset.column values
- Plot parameters
- Python plot guide
- Data visualization
- index-based plotting
- Programming
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /plot - Reference | OpenBB Terminal Docs" />

Plot data based on the index

### Usage

```python
plot [-v {}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| values | Dataset.column values to be displayed in a plot. Use comma to separate multiple | None | True | None |


---

## Examples

```python
(🦋) /forecast/ $ load aapl.csv

(🦋) /forecast/ $ plot appl.close
```
---
