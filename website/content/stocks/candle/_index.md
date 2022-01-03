```
usage: candle [-m] [--export {csv,json,xlsx}] [--sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}] [-d] [--raw] [-n NUM] [-h]
```

Shows historic data for the [loaded ticker](https://gamestonkterminal.github.io/GamestonkTerminal/stocks/load/) in an interactive chart that loads in a web browser. Static charts are also available through the optional '-m' argument. There is also the ability to retrieve and sort raw data sets based on the intraday interval and date window selected through the load command.

```
optional arguments:
  -m, --matplotlib      Flag to show matplotlib instead of interactive plot using plotly. (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  --sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}
                        Choose a column to sort by (default: )
  -d, --descending      Sort selected column descending (default: True)
  --raw                 Shows raw data instead of chart (default: False)
  -n NUM, --num NUM     Number to show if raw selected (default: 20)
  -h, --help            show this help message (default: False)
```

<img size="1400" alt="Feature Screenshot - candle it" src="https://user-images.githubusercontent.com/85772166/140820534-5d7b68d3-06b3-4afc-b299-9d3232ca2f79.png">
<img size="1400" alt="Feature Screenshot - candle raw" src="https://user-images.githubusercontent.com/85772166/140823989-b1ef3cb8-54ec-44ab-9f29-c9b68c1dc248.png">
