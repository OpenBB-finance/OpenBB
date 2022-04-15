```
usage: so [-t TARGET_RETURN] [-a] [-w WINDOW] [-h]
```

Provides the sortino ratio of the selected portfolio.

The sortino ratio is very similar to the sharpe ratio, but different in a crucial way. Sharpe ratio punishes the 
standard deviation of positive return. The sortino ratio only punishes standard deviation of negative returns. For
more, read: http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

```
optional arguments:
  -t TARGET_RETURN, --target TARGET_RETURN
                        Target return (default: 0)
  -a, --adjusted        If one should adjust the sortino ratio inorder to make it comparable to the sharpe ratio
                        (default: False)
  -w WINDOW, --window WINDOW
                        Rolling window length (default: 252)
  -h, --help            show this help message (default: False)
```
