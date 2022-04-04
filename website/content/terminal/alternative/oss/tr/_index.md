```
usage: tr [-h] [-c CATEGORIES] [-s {stars,forks}] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw] [-l LIMIT]
```

Display top repositories [Source: https://api.github.com]

```
optional arguments:
  -c, --categories      Filter by repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
  -s, --sortby          Sort repos by {stars, forks}. Default: stars
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

![cases](https://user-images.githubusercontent.com/46355364/153897646-99e4f73f-be61-4ed7-a31d-58e8695e7c50.png)
