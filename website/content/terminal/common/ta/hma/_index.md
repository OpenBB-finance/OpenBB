```
usage: hma [-l N_LENGTH] [-o N_OFFSET] [--export {csv,json,xlsx}] [-h]
```

The Hull Moving Average solves the age old dilemma of making a moving average more responsive to current price activity whilst maintaining curve
smoothness. In fact the HMA almost eliminates lag altogether and manages to improve smoothing at the same time.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        Window lengths. Multiple values indicated as comma separated values. (default: [10, 20])
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![hma](https://user-images.githubusercontent.com/46355364/154310988-2e97c166-a3b9-49ae-abcd-2c1b37309072.png)
