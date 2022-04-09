```
usage: pcr [-l {10,20,30,60,90,120,150,180}] [-s START] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Display put to call ratio for ticker [Source: AlphaQuery.com]

```
optional arguments:
  -l {10,20,30,60,90,120,150,180}, -length {10,20,30,60,90,120,150,180}
                        Window length to get (default: 30)
  -s START, --start START
                        Start date for plot (default: 2021-02-15 15:33:46.387854)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![pcr](https://user-images.githubusercontent.com/46355364/154286299-19ea423d-28e7-48d7-a5f3-621f0428fd4a.png)
