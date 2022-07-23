```
usage: chart [--vs VS] [-d DAYS] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Display chart for loaded coin. You can specify currency vs which you want to show chart and also number of days to get data for.

```
optional arguments:
  --vs VS               Currency to display vs coin (default: usd)
  -d DAYS, --days DAYS  Number of days to get data for (default: 30)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![chart](https://user-images.githubusercontent.com/46355364/154048383-6011faa5-0c68-41eb-b4dd-41923ff7da43.png)
