---
title: trans
description: OpenBB Terminal Function
---

# trans

Perform Transformer Forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.transformer_model.html

### Usage

```python
usage: trans [--d-model D_MODEL] [--nhead NHEAD] [--num_encoder_layers NUM_ENCODER_LAYERS] [--num_decoder_layers NUM_DECODER_LAYERS] [--dim_feedforward DIM_FEEDFORWARD] [--activation {relu,gelu}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| d_model | Number of expected features in inputs. | 64 | True | None |
| nhead | Number of head in the attention mechanism. | 4 | True | None |
| num_encoder_layers | The number of encoder leayers in the encoder. | 3 | True | None |
| num_decoder_layers | The number of decoder leayers in the encoder. | 3 | True | None |
| dim_feedforward | The dimension of the feedforward model. | 512 | True | None |
| activation | Number of LSTM layers. | relu | True | relu, gelu |
---

