```
usage: plot [-p] [-x {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-y {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-c {smile}] [-h] [--export {png,jpg,pdf,svg}]
```

Shows a plot for the given x and y variables.

```
optional arguments:
  -p, --put             Shows puts instead of calls (default: False)
  -x {ltd,s,lp,b,a,c,pc,v,oi,iv}, --x_axis {ltd,s,lp,b,a,c,pc,v,oi,iv}
                        ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility (default: None)
  -y {ltd,s,lp,b,a,c,pc,v,oi,iv}, --y_axis {ltd,s,lp,b,a,c,pc,v,oi,iv}
                        ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility (default: None)
  -c {smile}, --custom {smile}
                        Choose from already created graphs (default: None)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export figure into png, jpg, pdf, svg (default: )
```

Example:

```
2022 Feb 16, 09:37 (🦋) /stocks/options/ $ plot -p -x s -y iv
```

![plot](https://user-images.githubusercontent.com/46355364/154287325-97de8945-a44c-418d-9e88-5123ee70469f.png)
