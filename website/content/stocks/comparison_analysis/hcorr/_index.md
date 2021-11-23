```text
usage: corr [-t {o,h,l,c,a}] [-h]
```

A correlation heatmap for the selected tickers, using optional arguments described below. Scores range from +1 to -1 with 0 being completely neutral. 

```
optional arguments:
  -t {o,h,l,c,a}, --type {o,h,l,c,a}
                        Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. (default: a)
  -h, --help            show this help message (default: False)
```

<img size="1400" alt="Feature Screenshot - corr" src="https://user-images.githubusercontent.com/25267873/110699596-efc41b80-81e6-11eb-924f-8739058aa54e.png">
