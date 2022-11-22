---
title: tft
description: OpenBB Terminal Function
---

# tft

Perform TFT forecast (Temporal Fusion Transformer): https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html

### Usage

```python
usage: tft [--lstm-layers LSTM_LAYERS] [--num-attention-heads NUM_ATTENTION_HEADS] [--full-attention] [--hidden-continuous-size HIDDEN_CONTINUOUS_SIZE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| lstm_layers | Number of LSTM layers. | 1 | True | None |
| num_attention_heads | Number of attention heads. | 4 | True | None |
| full_attention | Whether to apply a multi-head attention query. | False | True | None |
| hidden_continuous_size | Default hidden size for processing continuous variables. | 8 | True | None |
---

