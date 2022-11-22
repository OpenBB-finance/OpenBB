---
title: rnn
description: OpenBB Terminal Function
---

# rnn

Perform RNN forecast (Vanilla RNN, LSTM, GRU): https://unit8co.github.io/darts/generated_api/darts.models.forecasting.rnn_model.html

### Usage

```python
usage: rnn [--hidden-dim HIDDEN_DIM] [--training_length TRAINING_LENGTH]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| hidden_dim | Size for feature maps for each hidden RNN layer (h_n) | 20 | True | None |
| training_length | The length of both input (target and covariates) and output (target) time series used during training. Generally speaking, training_length should have a higher value than input_chunk_length because otherwise during training the RNN is never run for as many iterations as it will during training. | 20 | True | None |
---

