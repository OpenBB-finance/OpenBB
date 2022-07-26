```
usage: mc [--dist {normal,lognormal}] [-d {AAPL,GME}] [-c TARGET_COLUMN] [-n N_DAYS] [--n-epochs N_EPOCHS] [-h] [--export EXPORT]
```

Perform Monte Carlo forecasting

```
optional arguments:

  --dist {normal,lognormal}
                        Whether to model returns or log returns (default: lognormal)
  -d {GME}, --target-dataset {GME}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 100)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about export' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 10:37 (🦋) /forecast/ $ mc GME
```
![mc](https://user-images.githubusercontent.com/72827203/180615284-f69c331c-1bf1-4b9b-9a57-a5ec1ac4f12f.png)
