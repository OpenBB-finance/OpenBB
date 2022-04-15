```
usage: sh [-r RFR] [-w WINDOW] [-h]
```

Provides the sharpe ratio of the selected portfolio.

The sharpe ratio is calculated by subtracting the risk-free rates from the return and then divide it by the risk, 
measured by the volatility. This gives the return per volatility point.

```
optional arguments:
  -r RFR, --rfr RFR     Risk free return (default: 0)
  -w WINDOW, --window WINDOW
                        Rolling window length (default: 252)
  -h, --help            show this help message (default: False)
```
![image](https://user-images.githubusercontent.com/75195383/163530796-6e21684d-82e4-40f9-9e4d-4c834028e707.png)
