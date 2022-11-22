```
usage: adx [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [--export {csv,json,xlsx}] [-h]
```

The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX). The values range from 0 to 100, but rarely get above 60. To
interpret the ADX, consider a high number to be a strong trend, and a low number, a weak trend.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 14)
  -s N_SCALAR, --scalar N_SCALAR
                        scalar (default: 100)
  -d N_DRIFT, --drift N_DRIFT
                        drift (default: 1)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![adx](https://user-images.githubusercontent.com/46355364/154309667-c67f6078-822f-452d-9853-ffffa9172670.png)
