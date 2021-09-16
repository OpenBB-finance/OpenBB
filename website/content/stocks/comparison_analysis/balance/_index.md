```text
usage: balance [-s L_SIMILAR] [-a L_ALSO] [-t 31-Dec-2020/2017] [-q]
```

Prints either yearly or quarterly balance statement the company, and compares it against similar companies.

```
optional arguments:
  -q, --quarter         Quarter financial data flag. (default: False)
  -t S_TIMEFRAME, --timeframe S_TIMEFRAME
                        Specify yearly/quarterly timeframe. Default is last. (default: None)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

<img width="1014" alt="Captura de ecrã 2021-03-20, às 09 10 53" src="https://user-images.githubusercontent.com/25267873/111865168-5373e480-895d-11eb-960f-b919e338ab83.png">
