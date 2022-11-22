```
usage: sh [-h] [-r REPO] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw]
```

Display a repo star history [Source: https://api.github.com]

```
optional arguments:
  -h, --help            show help message (default: False)
  -r --repo             Repository to search for star history. Format: org/repo, e.g., openbb-finance/openbbterminal
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```
