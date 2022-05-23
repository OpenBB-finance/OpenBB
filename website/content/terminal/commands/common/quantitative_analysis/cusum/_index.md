```text
usage: cusum [-t THRESHOLD] [-d DRIFT] [-h]
```

Cumulative Sum Control Chart. A stochastic wave used as a stock market breadth indicator in mid-to-long term analysis, it is a sequential analysis technique for step detection in a time-series. The threshold can be thought of as the level where the background noise is at or below the level of the true signal. 

See this paper for a deep dive: https://econpapers.wiwi.kit.edu/downloads/KITe_WP_62.pdf

```
optional arguments:
  -t THRESHOLD, --threshold THRESHOLD
                        threshold (default: 0.002988466304844406)
  -d DRIFT, --drift DRIFT
                        drift (default: 0.001494233152422203)
  -h, --help            show this help message (default: False)
```

![cusum](https://user-images.githubusercontent.com/46355364/154306207-d68f53f4-2f9a-4c1a-8e0e-b83d49938759.png)
