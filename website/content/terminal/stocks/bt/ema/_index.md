```
usage: ema [-l LENGTH] [--spy] [--no_bench] [-h] [--export {csv,json,xlsx}]
```

A simple investment strategy where stock is bought when Price > EMA(l)

```
optional arguments:
  -l LENGTH             EMA period to consider (default: 20)
  --spy                 Flag to add spy hold comparison (default: False)
  --no_bench            Flag to not show buy and hold comparison (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:

```
2022 Feb 16, 09:59 (🦋) /stocks/bt/ $ ema

Stat                 AboveEMA    MSFT Hold
-------------------  ----------  -----------
Start                2019-02-10  2019-02-10
End                  2022-02-15  2022-02-15
Risk-free rate       0.00%       0.00%

Total Return         53.12%      195.22%
Daily Sharpe         0.83        1.33
Daily Sortino        1.32        2.17
CAGR                 15.18%      43.21%
Max Drawdown         -18.91%     -28.04%
Calmar Ratio         0.80        1.54

MTD                  -7.29%      -3.38%
3m                   -15.90%     -10.43%
6m                   -6.26%      2.99%
YTD                  -9.30%      -10.66%
1Y                   0.12%       23.67%
3Y (ann.)            15.26%      42.12%
5Y (ann.)            -           -
10Y (ann.)           -           -
Since Incep. (ann.)  15.18%      43.21%

Daily Sharpe         0.83        1.33
Daily Sortino        1.32        2.17
Daily Mean (ann.)    15.98%      40.51%
Daily Vol (ann.)     19.35%      30.43%
Daily Skew           0.05        -0.13
Daily Kurt           5.04        10.90
Best Day             7.44%       14.22%
Worst Day            -6.19%      -14.74%

Monthly Sharpe       0.77        1.77
Monthly Sortino      1.71        4.66
Monthly Mean (ann.)  16.49%      36.33%
Monthly Vol (ann.)   21.45%      20.53%
Monthly Skew         0.08        0.21
Monthly Kurt         -1.20       -0.14
Best Month           11.83%      17.63%
Worst Month          -9.55%      -7.53%

Yearly Sharpe        0.62        0.83
Yearly Sortino       2.29        4.57
Yearly Mean          12.32%      28.12%
Yearly Vol           19.76%      33.95%
Yearly Skew          -0.98       -1.57
Yearly Kurt          -           -
Best Year            29.43%      52.48%
Worst Year           -9.30%      -10.66%

Avg. Drawdown        -4.56%      -2.78%
Avg. Drawdown Days   37.27       14.27
Avg. Up Month        6.15%       5.77%
Avg. Down Month      -4.59%      -4.11%
Win Year %           66.67%      66.67%
Win 12m %            92.31%      100.00%
```

![ema](https://user-images.githubusercontent.com/46355364/154291933-0243c1b1-29a9-4320-8efb-f589d3b7f220.png)
