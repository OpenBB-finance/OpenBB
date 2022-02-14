```
usage: lcsc [-d DAYS] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [-l LIMIT]
```

Display Luna circulating supply changes stats. [Source: Smartstake.io] Follow these steps to get the key token: 1. Head to
https://terra.smartstake.io/ 2. Right click on your browser and choose Inspect 3. Select Network tab (by clicking on the expand
button next to Source tab) 4. Go to Fetch/XHR tab, and refresh the page 5. Get the option looks similar to the following:
`listData?type=history&dayCount=30` 6. Extract the key and token out of the URL

```
optional arguments:
  -d DAYS, --days DAYS  Number of days to display. Default: 30 days (default: 30)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 5)
```
