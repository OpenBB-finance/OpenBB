```
usage: rolling [-b BENCHMARK] [-l LENGTH] [-r RF] [-h] [--export {png,jpg,pdf,svg}]
```
Show rolling portfolio metrics vs benchmark.

The plots shown are: cumulative returns vs benchmark, rolling volatility of portfolio and benchmark,
rolling sharpe ratio of portfolio and benchmark and the rolling beta with respect to the benchmark.

```
optional arguments:
  -b BENCHMARK, --benchmark BENCHMARK
                        Choose a ticker to be the benchmark (default: SPY)
  -l LENGTH, --length LENGTH
                        Length of rolling window (default: 60)
  -r RF, --rf RF        Set risk free rate for calculations. (default: 0.001)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export figure into png, jpg, pdf, svg (default: )

```

![rolling](https://user-images.githubusercontent.com/46355364/153899037-6868418f-bb6b-402f-900c-bbe627093440.png)
