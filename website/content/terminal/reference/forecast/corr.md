---
title: corr
description: The page provides information about the 'corr' function used to plot
  correlation coefficients of a given dataset. It describes parameters, usage examples
  and visual representation for a TSLA dataset.
keywords:
- corr
- plot correlation coefficients
- parameters
- dataset
- forecasting
- examples
- TSLA
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /corr - Reference | OpenBB Terminal Docs" />

Plot correlation coefficients.

### Usage

```python wordwrap
corr [-d {AAPL}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |


---

## Examples

```python
(🦋) /forecast/ $ load TSLA.csv

(🦋) /forecast/ $ corr TSLA
TODO: screen shot
```
---
