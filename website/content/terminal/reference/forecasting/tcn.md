---
title: tcn
description: OpenBB Terminal Function
---

# tcn

Perform TCN forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tcn_model.html

### Usage

```python
usage: tcn [--num-filters NUM_FILTERS] [--weight-norm WEIGHT_NORM] [--dilation-base DILATION_BASE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_filters | The number of filters in a convolutional layer of the TCN | 3 | True | None |
| weight_norm | Boolean value indicating whether to use weight normalization. | True | True | None |
| dilation_base | The base of the exponent that will determine the dilation on every level. | 2 | True | None |
---

