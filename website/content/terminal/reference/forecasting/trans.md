---
title: trans
description: OpenBB Terminal Function
---

# trans

Perform Transformer Forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.transformer_model.html

### Usage

```python
usage: trans [--d-model D_MODEL] [--nhead NHEAD]
             [--num_encoder_layers NUM_ENCODER_LAYERS]
             [--num_decoder_layers NUM_DECODER_LAYERS]
             [--dim_feedforward DIM_FEEDFORWARD] [--activation {relu,gelu}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| d_model | Number of expected features in inputs. | 64 | True | None |
| nhead | Number of head in the attention mechanism. | 4 | True | None |
| num_encoder_layers | The number of encoder layers in the encoder. | 3 | True | None |
| num_decoder_layers | The number of decoder layers in the encoder. | 3 | True | None |
| dim_feedforward | The dimension of the feedforward model. | 512 | True | None |
| activation | Number of LSTM layers. | relu | True | relu, gelu |
---

## Examples

```python
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:01 (🦋) /forecast/ $ trans GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:2300:00,  4.88it/s]
Transformer model obtains MAPE: 13.11%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 145.63   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 142.28   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 137.67   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 137.33   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 130.62   │
└─────────────────────┴────────────┘
```

![trans](https://user-images.githubusercontent.com/72827203/180615423-948cc67c-cead-4e13-9cab-c348bc4c86ab.png)

---

