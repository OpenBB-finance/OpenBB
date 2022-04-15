```
usage: sh [-r RFR] [-w WINDOW] [-h]
```

Provides the sharpe ratio of the selected stock.

The sharpe ratio is calculated by subtracting the risk-free rates from the return and then divide it by the risk, 
measured by the volatility. This gives the return per volatility point.

```
optional arguments:
  -r RFR, --rfr RFR     Risk free return (default: 0)
  -w WINDOW, --window WINDOW
                        Rolling window length (default: 252)
  -h, --help            show this help message (default: False)
```
![image](https://user-images.githubusercontent.com/75195383/163530426-77abe5ac-9c21-43e5-a975-5a37c7eb452f.png)
