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

```python wordwrap
plot [-v {AAPL.date,AAPL.open,AAPL.high,AAPL.low,AAPL.close,AAPL.adj_close,AAPL.volume,AAPL.dividends,AAPL.stock_splits}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| values | -v  --values | Dataset.column values to be displayed in a plot. Use comma to separate multiple | None | True | AAPL.date, AAPL.open, AAPL.high, AAPL.low, AAPL.close, AAPL.adj_close, AAPL.volume, AAPL.dividends, AAPL.stock_splits |


---

## Examples

```python
(🦋) /forecast/ $ load aapl.csv

(🦋) /forecast/ $ plot appl.close
```
---
