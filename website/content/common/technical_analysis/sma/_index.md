```
usage: sma [-l N_LENGTH] [-o N_OFFSET] [--export {csv,json,xlsx}] [-h]
```

Moving Averages are used to smooth the data in an array to help eliminate noise and identify trends. The Simple Moving Average is literally the
simplest form of a moving average. Each output value is the average of the previous n values. In a Simple Moving Average, each value in the time
period carries equal weight, and values outside of the time period are not included in the average. This makes it less responsive to recent changes
in the data, which can be useful for filtering out those changes.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        Window lengths. Multiple values indicated as comma separated values. (default: [20, 50])
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![sma](https://user-images.githubusercontent.com/25267873/108602304-36b5b280-7399-11eb-86fe-d490fb32aaff.png)
