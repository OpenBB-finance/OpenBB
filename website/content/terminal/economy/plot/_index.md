```
usage: plot [-y1 YAXIS1 [YAXIS1 ...]] [-y2 YAXIS2 [YAXIS2 ...]] [-h] [--export {csv,json,xlsx}] [--raw] [-l LIMIT]
```

This command can plot any data on two y-axes obtained from the macro, fred, index and treasury commands. To be able to use this data, use the -st argument available within these commands. For example 'macro -p GDP -c Germany
Netherlands -st' will store the data for usage in this command. Therefore, it allows you to plot different time series in one graph. You can use the 'options' command to show the required arguments to be entered. The example above
could be plotted the following way: 'plot -y1 Germany_GDP -y2 Netherlands_GDP' or 'plot -y1 Germany_GDP Netherlands_GDP'

```
optional arguments:
  -y1 YAXIS1 [YAXIS1 ...], --yaxis1 YAXIS1 [YAXIS1 ...]
                        Select the data you wish to plot on the first y-axis. You can select multiple variables here. (default: )
  -y2 YAXIS2 [YAXIS2 ...], --yaxis2 YAXIS2 [YAXIS2 ...]
                        Select the data you wish to plot on the second y-axis. You can select multiple variables here. (default: )
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Comparing Unemployment Rates and Consumer Confidence of France and Italy
```
2022 Mar 15, 07:43 (✨) /economy/ $ macro -p URATE CONF -c France Italy -s 2005-01-01 -st
2022 Mar 15, 07:45 (✨) /economy/ $ options
                   Options available to plot                    
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Command ┃ Options                                            ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ macro   │ France_URATE, France_CONF, Italy_URATE, Italy_CONF │
└─────────┴────────────────────────────────────────────────────┘

2022 Mar 15, 07:43 (✨) /economy/ $ plot -y1 France_URATE Italy_URATE -y2 France_CONF Italy_CONF
```
![Figure_1](https://user-images.githubusercontent.com/46355364/158633367-783d54eb-79ab-443f-af99-8a9ecadf5949.png)

Comparing U.S. treasury rate movements to the S&P 500
```
2022 Mar 15, 07:39 (✨) /economy/ $ treasury -m 1y 10y -s 2005-01-01 -st
2022 Mar 15, 07:40 (✨) /economy/ $ index sp500 -s 2005-01-01 -st
2022 Mar 15, 07:40 (✨) /economy/ $ plot -y1 sp500 -y2 Nominal_1-year Nominal_10-year
```
![Figure_2](https://user-images.githubusercontent.com/46355364/158633394-d948d909-d39b-4b05-9c5b-2e30b202cc32.png)
