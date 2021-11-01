```text
usage: unitroot [-r {c,ct,ctt,nc}] [-k {c,ct}] [--export {csv,json,xlsx}] [-h]
```

Unit root test / stationarity (ADF, KPSS)

```
optional arguments:
  -r {c,ct,ctt,nc}, --fuller_reg {c,ct,ctt,nc}
                        Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order (default: c)
  -k {c,ct}, --kps_reg {c,ct}
                        Type of regression. Can be ‘c’,’ct' (default: c)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
