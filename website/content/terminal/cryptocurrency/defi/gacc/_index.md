```
usage: gacc [-l LIMIT] [--cumulative] [-k {active,total}] [--descend] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```
Displays terra blockchain account growth history. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of days to show (default: 90)
  --cumulative          Show cumulative or discrete values. For active accounts only discrete value are available (default: True)
  -k {active,total}, --kind {active,total}
                        Total account count or active account count. Default: total (default: total)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![gacc](https://user-images.githubusercontent.com/46355364/154051829-8225869b-6ea8-434e-afd6-51b9c81e0ade.png)
