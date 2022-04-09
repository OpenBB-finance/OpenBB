```
usage: altindex [-s INITIAL_DATE]
                [-u END_DATE]
                [-p {30, 90, 365}]
                [--export {csv,json,xlsx}] [-h]
```

Display altcoin index overtime [Source: https://blockchaincenter.net]
If 75% of the Top 50 coins performed better than Bitcoin over periods of time (30, 90 or 365 days) it is Altcoin Season.
Excluded from the Top 50 are Stablecoins (Tether, DAI…) and asset backed tokens (WBTC, stETH, cLINK,…)

```
arguments:
  -s DATE --since DATE          Start date (default: 1 year before, e.g., 2021-01-01)
  -u DATE --until DATE          End date (default: current day, e.g., 2022-01-01)
  -p DAYS --period DAYS         Period of days to check performance (default: 365)
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```

![altindex](https://user-images.githubusercontent.com/46355364/154068454-43dbc146-31df-4b25-bf14-0b12284afc6d.png)
