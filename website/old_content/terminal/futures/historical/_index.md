```
usage: historical [-t TICKER] [-s START] [-e EXPIRY] [-h] [--export EXPORT] [--raw]
```

Display futures historical. [Source: YahooFinance]

```
optional arguments:
  -t TICKER, --ticker TICKER
                        Future ticker to display timeseries separated by comma when multiple, e.g.: BLK,QI (default: )
  -s START, --start START
                        Initial date. Default: 3 years ago (default: 2019-10-20 00:12:05.223144)
  -e EXPIRY, --expiry EXPIRY
                        Select future expiry date with format YYYY-MM (default: )
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
```

```
2022 Oct 18, 19:16 (🦋) /futures/ $ historical BLK
```

![blk](https://user-images.githubusercontent.com/25267873/196562549-1251b0fd-ca36-4e0f-bca6-b6bfe473effa.png)


```
2022 Oct 18, 19:17 (🦋) /futures/ $ historical BLK -e 2022-12
```

![Figure_31](https://user-images.githubusercontent.com/25267873/196562627-79f9ffa1-8582-457c-91e8-5c18d6d4304f.png)
