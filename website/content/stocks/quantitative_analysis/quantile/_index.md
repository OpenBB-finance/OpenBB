```
usage: quantile [-l N_LENGTH] [-q F_QUANTILE] [-h] [--export {csv,json,xlsx}]
```

The quantiles are values which divide the distribution such that there is a given proportion of observations below the
quantile. For example, the median is a quantile. The median is the central value of the distribution, such that half
the points are less than or equal to it and half are greater than or equal to it. By default, q is set at 0.5, which
effectively is median. Change q to get the desired quantile (0<q<1).

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 14)
  -q F_QUANTILE, --quantile F_QUANTILE
                        quantile (default: 0.5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
