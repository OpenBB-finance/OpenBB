```
usage: fisher [-l N_LENGTH] [--export {csv,json,xlsx}] [-h]
```

The Fisher Transform is a technical indicator created by John F. Ehlers that converts prices into a Gaussian normal distribution.1 The indicator
highlights when prices have moved to an extreme, based on recent prices. This may help in spotting turning points in the price of an asset. It also
helps show the trend and isolate the price waves within a trend.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 14)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
