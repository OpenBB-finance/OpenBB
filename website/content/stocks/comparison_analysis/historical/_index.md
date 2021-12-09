```text
usage: historical [-t {o,h,l,c,a}] [-s] [--export {csv,json,xlsx}] [-h]
```

Historical price comparison between the added tickers.

```
optional arguments:
  -t {o,h,l,c,a}, --type {o,h,l,c,a}
                        Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. (default: a)
  -s, --no-scale        Flag to not put all prices on same 0-1 scale (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

<img size="1400" alt="Feature Screenshot - historical" src="https://user-images.githubusercontent.com/25267873/110699590-ef2b8500-81e6-11eb-95e3-144793a83a80.png">
<img size="1400" alt="Feature Screenshot - historical normalized" src="https://user-images.githubusercontent.com/85772166/142901215-3cfd699c-adb2-4651-ab99-96cfc9ae807f.png">
