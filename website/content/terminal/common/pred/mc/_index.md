```
usage: mc [-d N_DAYS] [-n N_SIMS] [--dist {normal,lognormal}] [-h] [--export {png,jpg,pdf,svg}]
```

Perform Monte Carlo forecasting

```
optional arguments:
  -d N_DAYS, --days N_DAYS
                        Days to predict (default: 30)
  -n N_SIMS, --num N_SIMS
                        Number of simulations to perform (default: 100)
  --dist {normal,lognormal}
                        Whether to model returns or log returns (default: lognormal)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export figure into png, jpg, pdf, svg (default: )
```

![MC](https://user-images.githubusercontent.com/18151143/154814179-0cfe9c43-9395-41df-8d15-b8a1de1a8121.png)
