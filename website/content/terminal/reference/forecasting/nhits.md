---
title: nhits
description: OpenBB Terminal Function
---

# nhits

Perform nhits forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html

### Usage

```python
usage: nhits [--num-stacks NUM_STACKS] [--num-blocks NUM_BLOCKS] [--num-layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS]
             [--activation {ReLU,RReLU,PReLU,Softplus,Tanh,SELU,LeakyReLU,Sigmoid}] [--max_pool_1d]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_stacks | The number of stacks that make up the model | 3 | True | None |
| num_blocks | The number of blocks making up every stack | 1 | True | None |
| num_layers | The number of fully connected layers | 2 | True | None |
| layer_widths | The number of neurons in each layer | 3 | True | None |
| activation | The desired activation | ReLU | True | ReLU, RReLU, PReLU, Softplus, Tanh, SELU, LeakyReLU, Sigmoid |
| maxpool1d | Whether to use max_pool_1d or AvgPool1d | False | True | None |
---

