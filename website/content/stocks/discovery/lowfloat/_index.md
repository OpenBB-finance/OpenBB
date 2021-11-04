```
usage: lowfloat [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Request a list of stocks with floats under ten million shares, covering: NASDAQ, NYSE, AMEX, and OTC markets. Companies with low floats are easier targets for price manipulation; it takes fewer millions to move the needle. Many of these companies also accrue high levels of short interest. Source: (https://lowfloat.com)
```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of top stocks to print. (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img width="1400" alt="Feature Screeshot - lowfloat" src="https://user-images.githubusercontent.com/85772166/140385628-9fd091a7-7dc9-46e1-bdc1-42b87eb9a78b.png">
