```
usage: options [-h] [--export {csv,json,xlsx}] [--raw] [-l LIMIT]
```

Show the available options for the 'plot' command. To save data, use the command -st on 'macro', 'fred', 'index' and 'treasury'. You can use these commands to plot data on a multi-axes graoh. Furthermore, this command also allows you to
see and export all stored data.

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Example:

```
2022 Mar 16, 13:20 (🦋) /economy/ $ treasury -m 3y 5y -st
2022 Mar 16, 13:20 (🦋) /economy/ $ index vix sp500 dowjones -st
2022 Mar 16, 13:20 (🦋) /economy/ $ macro -p RGDP GDP -c Netherlands Germany -st
2022 Mar 16, 13:21 (🦋) /economy/ $ fred T10Y2y T10Y2YM -st
2022 Mar 16, 13:20 (🦋) /economy/ $ options
                         Options available to plot
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Command  ┃ Options                                                      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ treasury │ Nominal_3-year, Nominal_5-year                               │
├──────────┼──────────────────────────────────────────────────────────────┤
│ index    │ vix, sp500, dowjones                                         │
├──────────┼──────────────────────────────────────────────────────────────┤
│ macro    │ Netherlands_RGDP, Netherlands_GDP, Germany_RGDP, Germany_GDP │
├──────────┼──────────────────────────────────────────────────────────────┤
│ fred     │ T10Y2y, T10Y2YM                                              │
└──────────┴──────────────────────────────────────────────────────────────┘
```
