```
usage: lowfloat [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Print top stocks with lowest float. LowFloat.com provides a convenient sorted database of stocks which have a float of under 10 million shares.
Additional key data such as the number of outstanding shares, short interest, and company industry is displayed. Data is presented for the Nasdaq Stock
Market, the New York Stock Exchange, the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of top stocks to print. (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
