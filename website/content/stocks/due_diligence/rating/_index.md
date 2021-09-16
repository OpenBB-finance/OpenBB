```text
usage: rating [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell. The following fields are expected: P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]

```
optional arguments:
  -n N_NUM, --num N_NUM
                        number of last days to display ratings
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file
  -h, --help            show this help message
```

<img width="922" alt="rating" src="https://user-images.githubusercontent.com/25267873/108609444-d0935480-73c5-11eb-9f14-4fefa67f41ee.png">
