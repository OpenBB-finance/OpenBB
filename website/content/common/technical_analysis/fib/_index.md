```
usage: fib [-p PERIOD] [--start START] [--end END] [--export {csv,json,xlsx}] [-h]
```

Calculates the fibonacci retracement levels

The fibonocci retracement works by looking at a minimum and maximum point.  Between these values, there is typically support/resistance at
23.5 %, 38.2%, 50% and 61.8%.  Those values follow the golden ratio from the fibonocci sequence.

The `--start` and `--end` flags allow the user to select dates for the min and max points as your retracement levels.  Both flags are required if using.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Days to lookback for retracement (default: 120)
  --start START         Starting date to select (default: None)
  --end END             Ending date to select (default: None)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![Fib1](https://user-images.githubusercontent.com/18151143/127217240-0b4cd88b-8fd3-484f-941e-b02a0efe08dd.png)
