```
usage: hsi [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Browse a sorted database of stocks which have a short interest of over 20 percent. Additional key data such as the float, number of outstanding shares, and company industry is displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange, and the American Stock Exchange. Source: https://www.highshortinterest.com

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of top stocks to print. (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
