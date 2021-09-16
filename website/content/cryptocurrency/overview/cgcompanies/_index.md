```
usage: cgcompanies [-c {ethereum,bitcoin}] [-l] [--export {csv,json,xlsx}] [-h]
```

Track publicly traded companies around the world that are buying ethereum or bitcoin as part of corporate treasury: Rank, Company, Ticker, Country,
Total_Btc, Entry_Value, Today_Value, Pct_Supply, Url You can use additional flag --links to see urls to announcement about buying btc or eth by given
company. In this case you will see only columns like rank, company, url

```
optional arguments:
  -c {ethereum,bitcoin}, --coin {ethereum,bitcoin}
                        companies with ethereum or bitcoin (default: bitcoin)
  -l, --links           Flag to show urls. If you will use that flag you will see only rank, company, url columns (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
