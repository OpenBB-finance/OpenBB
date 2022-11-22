---
title: nbeats
description: OpenBB Terminal Function
---

# nbeats

Perform NBEATS forecast (Neural Bayesian Estimation of Time Series): https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nbeats.html

### Usage

```python
usage: nbeats [--num_stacks NUM_STACKS] [--num_blocks NUM_BLOCKS] [--num_layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_stacks | The number of stacks that make up the whole model. | 10 | True | None |
| num_blocks | The number of blocks making up every stack. | 3 | True | None |
| num_layers | The number of fully connected layers preceding the final forking layers in each block of every stack. | 4 | True | None |
| layer_widths | Determines the number of neurons that make up each fully connected layer in each block of every stack | 512 | True | None |
---

