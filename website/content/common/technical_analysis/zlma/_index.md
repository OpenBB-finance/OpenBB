```
usage: zlma [-l N_LENGTH] [-o N_OFFSET] [--export {csv,json,xlsx}] [-h]
```

The zero lag exponential moving average (ZLEMA) indicator was created by John Ehlers and Ric Way. The idea is do a regular exponential moving average (EMA) calculation but on a de-lagged data instead of doing it on the regular data. Data is de-lagged by removing the data from "lag" days ago thus removing (or attempting to) the cumulative effect of the moving average.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        Window lengths. Multiple values indicated as comma separated values. (default: [20])
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img width="1400" alt="Feature Screenshot - zlma" src="https://user-images.githubusercontent.com/85772166/144017029-f16b3275-9525-4496-a726-247a08b3ee7d.png">
