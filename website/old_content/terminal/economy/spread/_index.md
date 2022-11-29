```
usage: spread [-g {G7,PIIGS,EZ,AMERICAS,EUROPE,ME,APAC,AFRICA}]
              [-c COUNTRIES [COUNTRIES ...]] [-m MATURITY] [--change CHANGE]
              [-h] [--export EXPORT] [--raw]
```

Generate bond spread matrix.

```
  -g {G7,PIIGS,EZ,AMERICAS,EUROPE,ME,APAC,AFRICA}, --group {G7,PIIGS,EZ,AMERICAS,EUROPE,ME,APAC,AFRICA}
                        Show bond spread matrix for group of countries.
                        (default: G7)
  -c COUNTRIES [COUNTRIES ...], --countries COUNTRIES [COUNTRIES ...]
                        Show bond spread matrix for explicit list of
                        countries. (default: None)
  -m MATURITY, --maturity MATURITY
                        Specify maturity to compare rates. (default: 10Y)
  --change CHANGE       Get matrix of 1 day change in rates or spreads.
                        (default: False)
  --color {rgb,binary,openbb}
                        Set color palette on heatmap. (default: openbb)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
```
