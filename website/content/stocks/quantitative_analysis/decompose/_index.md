```text
usage: decompose [-m] [--export {csv,json,xlsx}] [-h]
```

Decompose time series as:
- Additive Time Series = Level + CyclicTrend + Residual + Seasonality
- Multiplicative Time Series = Level * CyclicTrend *
Residual * Seasonality

```
optional arguments:
  -m, --multiplicative  decompose using multiplicative model instead of additive (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![decompose](https://user-images.githubusercontent.com/25267873/112729282-4c337480-8f23-11eb-913c-f30e5c0ef459.png)

<img width="972" alt="Captura de ecrã 2021-03-27, às 17 32 05" src="https://user-images.githubusercontent.com/25267873/112729352-9157a680-8f23-11eb-9db7-6ecc760a4a25.png">
