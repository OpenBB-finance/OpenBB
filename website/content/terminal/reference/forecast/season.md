---
title: season
description: Meta description for the 'season' function in Docusaurus. This function
  helps to display and understand the seasonality for a given column in a dataset,
  providing options for customization such as time lag, maximal lag order, and confidence
  interval.
keywords:
- docusaurus
- season
- dataset
- seasonality
- time lag
- maximal lag order
- confidence interval
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /season - Reference | OpenBB Terminal Docs" />

The seasonality for a given column

### Usage

```python
season [-v {}] [-m M] [--max_lag MAX_LAG] [-a ALPHA]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| values | Dataset.column values to be displayed in a plot | None | True | None |
| m | A time lag to highlight on the plot | None | True | None |
| max_lag | The maximal lag order to consider | 24 | True | None |
| alpha | The confidence interval to display | 0.05 | True | None |


---

## Examples

```python
(🦋) /forecast/ $ load TSLA.csv

(🦋) /forecast/ $ season TSLA.volume
TODO: screen shot
```
---
