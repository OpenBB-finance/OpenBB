```
usage: knn [--neighbors N_NEIGHBORS] [--no_shuffle] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT]
           [-i INPUT_CHUNK_LENGTH] [-e S_END_DATE] [-j N_JUMPS] [-h] [--export EXPORT]
```

K nearest neighbors is a simple algorithm that stores all available cases and predict the numerical target based on a
similarity measure (e.g. distance functions).

```
optional arguments:

  --neighbors N_NEIGHBORS
                        number of neighbors to use on the algorithm. (default: 20)
  --no_shuffle          Specify if shuffling validation inputs. (default: True)
  -d {AAPL}, --target-dataset {AAPL}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  -t TRAIN_SPLIT, --train-split TRAIN_SPLIT
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  -i INPUT_CHUNK_LENGTH, --input-chunk-length INPUT_CHUNK_LENGTH
                        Number of past time steps for forecasting module at prediction time. (default: 14)
  -e S_END_DATE, --end S_END_DATE
                        The end date (format YYYY-MM-DD) to select for testing (default: None)
  -j N_JUMPS, --jumps N_JUMPS
                        number of jumps in training data. (default: 1)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about export' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 10:37 (🦋) /forecast/ $ mc GME
Training on 628 sequences of length 14.  Using 112 sequences  of length 14 for validation

       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 126.60   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 126.36   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 126.79   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 125.76   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 125.22   │
└─────────────────────┴────────────┘
```
![knn](https://user-images.githubusercontent.com/72827203/180615274-eb721541-ea32-4506-8cf5-3e555ca5cb62.png)
