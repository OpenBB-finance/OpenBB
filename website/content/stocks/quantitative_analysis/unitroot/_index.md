```
usage: unitroot [-r {c,ct,ctt,nc}] [-k {c,ct}] [-h] [--export {csv,json,xlsx}]
```

Unit root test / stationarity (ADF, KPSS)

```
optional arguments:
  -r {c,ct,ctt,nc}, --fuller_reg {c,ct,ctt,nc}
                        Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order (default: c)
  -k {c,ct}, --kps_reg {c,ct}
                        Type of regression. Can be ‘c’,’ct' (default: c)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
